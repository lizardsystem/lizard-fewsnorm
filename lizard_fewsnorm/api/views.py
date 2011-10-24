from djangorestframework.views import View


class AdapterView(View):
    """
    Class based REST view for adapter.
    """
    def __init__(self, resource, *args, **kwargs):
        return super(AdapterView, self).__init__(*args, **kwargs)

    def get(self, request):
        return {'ja': 'ha'}
