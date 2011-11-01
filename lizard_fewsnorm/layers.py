import os
import mapnik
import math
import datetime

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from lizard_map import coordinates
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache
from lizard_fewsnorm.models import Parameters
from lizard_fewsnorm.models import ParameterGroups
from lizard_fewsnorm.models import Locations
from lizard_fewsnorm.models import TimeseriesKeys
from lizard_fewsnorm.models import TimeseriesValuesAndFlags

from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager
from lizard_map.adapter import Graph

import logging
logger = logging.getLogger(__name__)


class AdapterFewsNorm(WorkspaceItemAdapter):
    def __init__(self, *args, **kwargs):
        """
        TODO: make fews_norm_source_slug optional (or leave it away).
        """
        super(AdapterFewsNorm, self).__init__(*args, **kwargs)
        self.parameter_id = self.layer_arguments.get('parameter_id', None)
        self.module_id = self.layer_arguments.get('module_id', None)
        self.fews_norm_source_slug = self.layer_arguments.get(
            'fews_norm_source_slug', None)
        self.fewsnorm_source = FewsNormSource.objects.get(
            slug=self.fews_norm_source_slug)
        self.parameter = self.fewsnorm_source.o(Parameters).get(
            id=self.parameter_id)

    def _default_mapnik_style(self):
        icon_style = {
            'icon': 'meetpuntPeil.png',
            'mask': ('meetpuntPeil_mask.png', ),
            'color': (1.0, 0.5, 0.0, 1.0)
            }
        symbol_manager = SymbolManager(
            ICON_ORIGINALS,
            os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
        output_filename = symbol_manager.get_symbol_transformed(
            icon_style['icon'], **icon_style)
        output_filename_abs = os.path.join(
            settings.MEDIA_ROOT, 'generated_icons', output_filename)

        # use filename in mapnik pointsymbolizer
        point_looks = mapnik.PointSymbolizer(
            str(output_filename_abs), 'png', 16, 16)
        point_looks.allow_overlap = True
        layout_rule = mapnik.Rule()
        layout_rule.symbols.append(point_looks)

        area_looks = mapnik.PolygonSymbolizer(mapnik.Color("#ff8877"))
        line_looks = mapnik.LineSymbolizer(mapnik.Color('#997766'), 1)
        layout_rule.symbols.append(area_looks)
        layout_rule.symbols.append(line_looks)

        # We use 'class' to filter the correct style for the locations
        # layout_rule.filter = mapnik.Filter(
        #     "[style] = '%s'" % str(point_style_name))

        point_style = mapnik.Style()
        point_style.rules.append(layout_rule)

        return point_style

    def _parameter_group(self):
        """
        Returns ParameterGroups object of self.parameter
        """
        groupkey = self.parameter.groupkey.groupkey
        parameter_group = self.fewsnorm_source.o(ParameterGroups).get(groupkey=groupkey)
        return parameter_group

    def _unit(self):
        """
        Returns parameter group unit
        """
        unit = self._parameter_group().unit
        if unit:
            return unit
        else:
            return "UNKOWN"

    def layer(self, layer_ids=None, request=None):
        """Generate layers and styles

        The layer is filtered using fews_norm_source_slug,
        parameter_id and module_id
        """
        styles = {}

        query = (
            """
          (select geometry from
             lizard_geo_geoobject as geoobject,
             lizard_fewsnorm_geolocationcache as loc,
             lizard_fewsnorm_fewsnormsource as source,
             lizard_fewsnorm_parametercache as par,
             lizard_fewsnorm_modulecache as mod,
             lizard_fewsnorm_geolocationcache_parameter as geoloc_par where
               loc.geoobject_ptr_id = geoobject.id and
               loc.fews_norm_source_id = source.id and
               source.slug = '%s' and
               loc.geoobject_ptr_id = geoloc_par.geolocationcache_id and
               geoloc_par.parametercache_id = par.id and
               par.ident = '%s'
           ) data""" % (self.fews_norm_source_slug, self.parameter_id))
        # query = (
        #     """(select geometry from
        #          lizard_geo_geoobject as geoobject,
        #          lizard_fewsnorm_geolocationcache as loc
        #          where loc.geoobject_ptr_id = geoobject.id
        #     ) data""")
        # query = (
        #     """(select geometry from
        #          lizard_geo_geoobject
        #     ) data""")

        default_database = settings.DATABASES['default']
        datasource = mapnik.PostGIS(
            host=default_database['HOST'],
            port=default_database['PORT'],
            user=default_database['USER'],
            password=default_database['PASSWORD'],
            dbname=default_database['NAME'],
            table=query.encode('ascii')
            )

        layer = mapnik.Layer("FewsNorm", coordinates.WGS84)
        layer.datasource = datasource

        style_name = 'lizard_fewsnorm::default'
        styles[style_name] = self._default_mapnik_style()
        layer.styles.append(style_name)
        layers = [layer, ]

        return layers, styles

    def search(self, google_x, google_y, radius=None):
        """Search by coordinates. Return list of dicts for matching
        items.
        """
        def distance(x1, y1, x2, y2):
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        x, y = coordinates.google_to_wgs84(google_x, google_y)
        pnt = GEOSGeometry(Point(x, y),srid=4326)
        locations = GeoLocationCache.objects.filter(
            geometry__distance_lte=(pnt, D(m=radius * 0.3)),
            parameter=ParameterCache.objects.get(ident=self.parameter_id))
        result = []
        for location in locations:
            location_google_x, location_google_y =  coordinates.wgs84_to_google(
                location.geometry.get_x(),
                location.geometry.get_y())
            dist = distance(google_x, google_y, location_google_x, location_google_y)
            logger.debug(location.__unicode__())
            result.append(
                {'distance': dist,
                 'name': location.__unicode__(),
                 'shortname': location.shortname,
                 'workspace_item': self.workspace_item,
                 'identifier': {'ident': location.ident},
                 'google_coords': (location_google_x, location_google_y)})
        return result

    def value_aggregate(self, identifier, aggregate_functions,
                        start_date=None, end_date=None):
        return self.value_aggregate_default(
            identifier, aggregate_functions_start_date, end_date)

    def location(self, ident, layout=None):
        """
        {'object': <...>,
        'google_x': x coordinate in google,
        'google_y': y coordinate in google,
        'workspace_item': <...>,
        'identifier': {...},
        'grouping_hint': optional unique group identifier, i.e. unit m3/s}
        """
        location = GeoLocationCache.objects.get(ident=ident)
        return {'name': location.__unicode__(),
                'shortname': location.shortname,
                'workspace_item': self.workspace_item,
                'identifier': {'location': location.ident}}

    def values(self, identifier, start_date, end_date):
        """
        Selects timeseries of given location and parameter:
        - look up fewsnorm source in FewsNormSource with self.fews_norm_source_slug
        - look up parameter in Parameters with self.parameter_id
        - foor each location in identifiers
           - look up location im Locations with identifier
           - look up timeserieskey in TimeseriesKey with location and paremater
           - look up timeseries with timeserieskey
        """
        location = self.fewsnorm_source.o(Locations).get(id=identifier['ident'])
        serieskey_filter = {'locationkey': location, 'parameterkey': self.parameter}
        print self.fewsnorm_source.o(TimeseriesKeys).filter(**serieskey_filter)
        serieskey = self.fewsnorm_source.o(TimeseriesKeys).get(**serieskey_filter)

        timeseries_filter = {'serieskey': serieskey,
                             'datetime__gte': start_date,
                             'datetime__lte': end_date}
        timeseriedata = self.fewsnorm_source.o(TimeseriesValuesAndFlags).order_by(
            "datetime").filter(**timeseries_filter)
        result = []
        for timeserie_row in timeseriedata:
            result.append({
                    'value': timeserie_row.scalarvalue,
                    'datetime': timeserie_row.datetime,
                    })
        return result

    def image(self, identifiers=None, start_date=None, end_date=None,
              width=None, height=None, layout_extra=None):
        """
        Create graph of given parameters
        for all locations in identifiers object.

        """
        today = datetime.datetime.now()
        graph = Graph(start_date, end_date,
                      width=width, height=height, today=today)
        graph.axes.grid(True)
        graph.add_today()
        # Draw graph lines with extra's
        title = None
        y_min, y_max = None, None
        legend = None

        for identifier in identifiers:
            timeseriesdata = self.values(identifier, start_date, end_date)
            dates = []
            values = []
            for series_row in timeseriesdata:
                dates.append(series_row['datetime'])
                values.append(series_row['value'])
            if len(values) < 30:
                plot_style = 'o-'
            else:
                plot_style = '-'

            # graph.axes.plot(dates, values, plot_style,
            #                 lw=1, label=identifier['ident'])
            graph.axes.bar(dates, values, plot_style,
                            width=0, label=identifier['ident'])
            graph.axes.set_ylabel(self._unit())

            graph.legend()
            graph.axes.legend_.draw_frame(False)

        return graph.http_png()


    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        return self.html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)

