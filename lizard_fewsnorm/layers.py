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
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import Parameter
from lizard_fewsnorm.models import ParameterGroups
from lizard_fewsnorm.models import Series
from lizard_fewsnorm.models import Timesteps
from lizard_fewsnorm.models import Event
from lizard_fewsnorm.models import TimeSeriesCache

from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager
from lizard_map.adapter import Graph

import logging
logger = logging.getLogger(__name__)


TIME_STEPS = {'SETS1440': 1440}


class AdapterFewsNorm(WorkspaceItemAdapter):
    """
    Adapter for fewsnorm databases.

    - parameter_id is needed for search and layer. It is provided in
      the identifier for image.

    - optionally provide module_id, it is not used yet.

    - optionally provide fews_norm_source_slug when using the layer
      function (should be made optional in layer as well).
    """

    @classmethod
    def identifiers(self):
        """Return all possible identifiers in a list.
        """
        result = []
        for timeserie in TimeSeriesCache.objects.all():
            result.append({
                    'ident': timeserie.geolocationcache.ident,
                    'parameter_id': timeserie.parametercache.ident,
                    'module_id': timeserie.modulecache.ident})
        return result

    @classmethod
    def _unit(cls, fewsnorm_source, parameter_id):
        """
        Return parameter group unit
        """
        parameter = fewsnorm_source.o(Parameter).get(
            id=parameter_id)
        groupkey = parameter.groupkey.groupkey
        parameter_group = fewsnorm_source.o(ParameterGroups).get(
            groupkey=groupkey)
        if parameter_group.unit:
            return parameter_group.unit
        else:
            return "UNKNOWN"

    @classmethod
    def _fewsnorm_source(cls, ident):
        """Look up fewsnorm_source object using provided location ident.
        """
        location_cache = GeoLocationCache.objects.get(
            ident=ident)
        fewsnorm_source = location_cache.fews_norm_source
        return fewsnorm_source

    def __init__(self, *args, **kwargs):
        """
        """
        super(AdapterFewsNorm, self).__init__(*args, **kwargs)
        self.parameter_id = self.layer_arguments.get('parameter_id', None)
        self.module_id = self.layer_arguments.get('module_id', None)
        self.fews_norm_source_slug = self.layer_arguments.get(
            'fews_norm_source_slug', None)

    def _default_mapnik_style(self):
        """
        Default implementation, not using any external django objects.

        TODO: make configurable.
        """
        icon_style = {
            'icon': 'meetpuntPeil.png',
            'mask': ('meetpuntPeil_mask.png', ),
            'color': (1.0, 0.5, 0.0, 1.0)}
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

    def _series(self, identifier, fewsnorm_source):
        series = Series.objects.using(fewsnorm_source.database_name).get(
            location__id=identifier['ident'],
            parameter__id=self.parameter_id,
            moduleinstance__id=self.module_id)
        return series

    def _timestep(self, identifier, fewsnorm_source):
        """
        Return value of matched timestep in minutes
        otherwise return None.
        """
        timestepkey = Series.objects.using(fewsnorm_source.database_name).get(
            series=self._series(
                identifier, fewsnorm_source).serieskey).timestepkey
        timestep = Timesteps.objects.using(fewsnorm_source.database_name).get(
            timestepkey=timestepkey.timestepkey)
        return TIME_STEPS.get(timestep.id, None)

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
             lizard_fewsnorm_timeseriescache as ts_cache where
               loc.geoobject_ptr_id = geoobject.id and
               loc.fews_norm_source_id = source.id and
               source.slug = '%s' and
               loc.geoobject_ptr_id = ts_cache.geolocationcache_id and
               ts_cache.parametercache_id = par.id and
               par.ident = '%s' and
               ts_cache.modulecache_id = mod.id and
               mod.ident = '%s'
           ) data""" % (self.fews_norm_source_slug, self.parameter_id,
                        self.module_id))
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
            table=query.encode('ascii'))

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

        Assumes that the geometries are stored as wgs84.

        Note that self.parameter_id must be filled.
        """
        def distance(x1, y1, x2, y2):
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        #x, y = coordinates.google_to_wgs84(google_x, google_y)
        #pnt = GEOSGeometry(Point(x, y), srid=4326)
        pnt = GEOSGeometry(Point(google_x, google_y), srid=900913)
        locations = GeoLocationCache.objects.filter(
            geometry__distance_lte=(pnt, D(m=radius * 0.3)),
            parameter__ident=self.parameter_id,
            module__ident=self.module_id)

        result = []
        for location in locations:
            location_google_x, location_google_y = coordinates.wgs84_to_google(
                location.geometry.get_x(),
                location.geometry.get_y())
            dist = distance(
                google_x, google_y, location_google_x, location_google_y)
            logger.debug(location.__unicode__())
            result.append(
                {'distance': dist,
                 'name': location.__unicode__(),
                 'shortname': location.shortname,
                 'workspace_item': self.workspace_item,
                 'identifier': {
                        'ident': location.ident,
                        'parameter_id': self.parameter_id},
                 'google_coords': (location_google_x, location_google_y)})
        return result

    # def value_aggregate(self, identifier, aggregate_functions,
    #                     start_date=None, end_date=None):
    #     return self.value_aggregate_default(
    #         identifier, aggregate_functions_start_date, end_date)

    def location(self, ident, parameter_id, layout=None):
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
                'identifier': {'ident': ident,
                               'parameter_id': parameter_id},
                'object': location}

    def values(self, identifier, start_date, end_date, fewsnorm_source=None):
        """
        Return timeseries data of given location and parameter.

        Optionally provide fewsnorm_source.

        - look up fewsnorm source in FewsNormSource with
          self.fews_norm_source_slug

        - look up parameter in Parameters with self.parameter_id

        - foor each location in identifiers

           - look up location im Locations with identifier

           - look up timeserieskey in TimeseriesKey with location and
             parameter

           - look up timeseries with timeserieskey
        """

        # Go from default database to fewsnorm database.
        if fewsnorm_source is None:
            fewsnorm_source = AdapterFewsNorm._fewsnorm_source(
                identifier['ident'])

        series = self._series(identifier, fewsnorm_source)

        events = Event.objects.using(
            fewsnorm_source.database_name).order_by("timestamp").filter(
            series=series,
            timestamp__gte=start_date,
            timestamp__lte=end_date)
        result = []
        for event in events:
            result.append({
                    'value': event.value,
                    'datetime': event.timestamp,
                    'flag': event.flag,
                    })
        return result

    # def _plot_bar(self, graph, dates, values, identifier,
    # start_date, end_date):
    #     """
    #     Calculates the width of bar and bar chart only for equidistant
    # timeseries.
    #     """

    #     time_delta = (end_date - start_date).days
    #     timestep = self._timestep(identifier)
    #     if time_delta > 0 and timestep != None:
    #         bar_width = timestep / time_delta / 24
    #         graph.axes.bar(dates, values, edgecolor=random.choice(colorList),
    #                        width=bar_width, label=identifier['ident']
    #                       )

    def image(self, identifiers=None, start_date=None, end_date=None,
              width=None, height=None, layout_extra=None):
        """
        Create graph of given parameters
        for first identifier in identifiers object.
        Plots lines and bar charts depends on layout_extra['type'].
        Draws bar charts only for equidistant timeseries.
        """
        if layout_extra == None or len(layout_extra) <= 0:
            layout_extra = {
                "lines": [{"style": "-", "y-position": 1.97,
                           "color": "red", "width": 3, "name": "L1"},
                          {"style": "--", "y-position": 2.12,
                           "color": "green", "width": 3, "name": "L2"}],
                "type": "line",
                "style": '-',
                "width": 1}

        today = datetime.datetime.now()
        graph = Graph(start_date, end_date,
                      width=width, height=height, today=today)
        graph.axes.grid(True)
        graph.add_today()
        # Draw graph lines with extra's
        #title = None
        y_min, y_max = None, None
        #legend = None
        for identifier in identifiers:
            fewsnorm_source = self._fewsnorm_source(identifier['ident'])
            events = self.values(
                identifier, start_date, end_date,
                fewsnorm_source=fewsnorm_source)

            dates = []
            values = []
            for event in events:
                dates.append(event['datetime'])
                values.append(event['value'])
            if layout_extra.get('type') == "line":
                graph.axes.plot(dates,
                                values,
                                ls=layout_extra.get('style'),
                                lw=layout_extra.get('width'),
                                label=identifier['ident'])
            elif layout_extra.get('type') == "bar":
                time_delta = (end_date - start_date).days
                timestep = self._timestep(identifier, fewsnorm_source)
                if time_delta > 0 and timestep != None:
                    bar_width = (float(timestep) / 60 / 24) / float(time_delta)
                    graph.axes.bar(dates, values,
                                   edgecolor='Red',
                                   width=bar_width, label=identifier['ident'])
                for line in layout_extra.get('lines'):
                    graph.axes.axhline(y=line.get('y-position'),
                                       ls=line.get('style'),
                                       color=line.get('color'),
                                       lw=line.get('width'),
                                       label=line.get('name'))
            break

        graph.axes.set_ylabel(
            AdapterFewsNorm._unit(fewsnorm_source, self.parameter_id))

        graph.legend()
        graph.axes.legend_.draw_frame(False)

        return graph.http_png()

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        return self.html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)
