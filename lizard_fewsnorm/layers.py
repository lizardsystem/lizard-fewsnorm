import os
import mapnik
import math

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from lizard_map import coordinates
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache

from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager

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
            geometry__distance_lte=(pnt, D(m=radius * 0.3)))
        print locations
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

    def image(self, identifiers=None, start_date=None, end_date=None,
              width=None, height=None, layout_extra=None):
        """
        Create graph of given parameters.
        """
        # today_site_tz = self.tz.localize(datetime.datetime.now())
        # start_date_utc, end_date_utc = self._to_utc(start_date, end_date)
        # graph = RainappGraph(start_date_utc,
        #                      end_date_utc,
        #                      width=width,
        #                      height=height,
        #                      today=today_site_tz,
        #                      tz=self.tz)

        # # Gets timeseries, draws the bars, sets  the legend
        # for identifier in identifiers:
        #     location_name = self._get_location_name(identifier)
        #     cached_value_result = self._cached_values(identifier,
        #                                               start_date_utc,
        #                                               end_date_utc)
        #     dates_site_tz = [row['datetime'].astimezone(self.tz)
        #                  for row in cached_value_result]
        #     values = [row['value'] for row in cached_value_result]
        #     units = [row['unit'] for row in cached_value_result]
        #     unit = ''
        #     if len(units) > 0:
        #         unit = units[0]
        #     if values:
        #         unit_timedelta = UNIT_TO_TIMEDELTA.get(unit, None)
        #         if unit_timedelta:
        #             # We can draw bars corresponding to period
        #             bar_width = graph.get_bar_width(unit_timedelta)
        #             offset = -1 * unit_timedelta
        #             offset_dates = [d + offset for d in dates_site_tz]
        #         else:
        #             # We can only draw spikes.
        #             bar_width = 0
        #             offset_dates = dates_site_tz
        #         graph.axes.bar(offset_dates,
        #                        values,
        #                        edgecolor='blue',
        #                        width=bar_width,
        #                        label=location_name)
        #     graph.set_ylabel(unit)
        #     # graph.legend()
        #     graph.suptitle(location_name)

        #     # Use first identifier and breaks the loop
        #     break

        # graph.responseobject = HttpResponse(content_type='image/png')

        # return graph.png_response()
        pass

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        return self.html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)

