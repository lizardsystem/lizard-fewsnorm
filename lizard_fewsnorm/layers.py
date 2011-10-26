import os
import mapnik

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry

from lizard_map import coordinates
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_fewsnorm.models import FewsNormSource

from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager


class AdapterFewsNorm(WorkspaceItemAdapter):
    def __init__(self, *args, **kwargs):
        super(AdapterFewsNorm, self).__init__(*args, **kwargs)
        self.parameter_id = self.layer_arguments['parameter_id']
        self.module_id = self.layer_arguments['module_id']
        self.fews_norm_source_slug = self.layer_arguments[
            'fews_norm_source_slug']

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
        parameter_id and module_id"""
        styles = {}
        #fews_norm_source = FewsNormSource(slug=self.fews_norm_source_slug)
        # query = (
        #     """
        #   (select geometry from
        #      lizard_geo_geoobject as geoobject,
        #      lizard_fewsnorm_geolocationcache as loc,
        #      lizard_fewsnorm_fewsnormsource as source where
        #        loc.geoobject_ptr_id = geoobject.id and
        #        loc.fews_norm_source_id = source.id and
        #        source.slug = '%s'
        #    ) data""" % self.fews_norm_source_slug)
        # query = (
        #     """(select geometry from
        #          lizard_geo_geoobject as geoobject,
        #          lizard_fewsnorm_geolocationcache as loc
        #          where loc.geoobject_ptr_id = geoobject.id
        #     ) data""")
        query = (
            """(select geometry from
                 lizard_geo_geoobject
            ) data""")

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
        print "+++++++++++++++++++++++++++++++++++++++++++"
        print "%s | %s | %s" % (google_x, google_y, radius)
        x, y = coordinates.google_to_rd(google_x, google_y)
        print "%s | %s | %s" % (x, y, radius)
        pnt = Point(x, y)

    def value_aggregate(self, identifier, aggregate_functions,
                        start_date=None, end_date=None):
        return self.value_aggregate_default(
            identifier, aggregate_functions_start_date, end_date)

    def location(self, identifier=None, layout=None):
        """
        {'object': <...>,
        'google_x': x coordinate in google,
        'google_y': y coordinate in google,
        'workspace_item': <...>,
        'identifier': {...},
        'grouping_hint': optional unique group identifier, i.e. unit m3/s}
        """
        pass

    def image(self, identifiers=None, start_date=None, end_date=None,
              width=None, height=None, layout_extra=None):
        """
        Create graph of given parameters.
        """
        pass

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        return self.html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)

