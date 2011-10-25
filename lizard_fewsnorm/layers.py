from lizard_map.workspace import WorkspaceItemAdapter


class AdapterFewsNorm(WorkspaceItemAdapter):
    def __init__(self, *args, **kwargs):
        super(AdapterFewsNorm, self).__init__(*args, **kwargs)
        # Something with layer_arguments specific for FewsNorm

    def layer(self, layer_ids=None, request=None):
        """Generate layers and styles"""
        pass

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

