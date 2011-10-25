import mapnik

from django.conf import settings

from lizard_map.workspace import WorkspaceItemAdapter
from lizard_fewsnorm.models import FewsNormSource


class AdapterFewsNorm(WorkspaceItemAdapter):
    def __init__(self, *args, **kwargs):
        super(AdapterFewsNorm, self).__init__(*args, **kwargs)
        self.parameter_id = self.layer_arguments['parameter_id']
        self.module_id = self.layer_arguments['module_id']
        self.fews_norm_source_slug = self.layer_arguments[
            'fews_norm_source_slug']

    def layer(self, layer_ids=None, request=None):
        """Generate layers and styles

        The layer is filtered using fews_norm_source_slug,
        parameter_id and module_id"""
        layers = []
        styles = {}
        #fews_norm_source = FewsNormSource(slug=self.fews_norm_source_slug)
        query = (
            """
          (select geometry from lizard_fewsnorm_geolocationcache as loc,
             lizard_fewsnorm_fewsnormsource as source where
               loc.fews_norm_source_id = source.id and
               source.slug = '%s'
           ) data""" % self.fews_norm_source_slug)

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

        return layers, styles

    def search(self, x, y, radius=None):
        """Search by coordinates. Return list of dicts for matching
        items.
        """
        pass

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

