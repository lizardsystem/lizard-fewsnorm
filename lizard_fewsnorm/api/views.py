from djangorestframework.views import View
from django.core.urlresolvers import reverse

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache


class RootView(View):
    """
    Class based REST root view.
    """
    def get(self, request):
        return {
            'adapter': {
                'name': 'adapter-fewsnorm',
                'url': reverse("lizard_fewsnorm_api_adapter_choice")},
            'locations': {
                'name': 'locations',
                'url': reverse("lizard_fewsnorm_api_location")},
            'parameters': {
                'name': 'parameters',
                'url': reverse("lizard_fewsnorm_api_parameter")}
            }

class LocationView(View):
    """
    Locations
    """
    def get(self, request, *args, **kwargs):
        return [{'ident': location.ident,
                 'url': location.api_url()}
                for location in GeoLocationCache.objects.all()]


class ParameterView(View):
    """
    Parameters
    """
    def get(self, request, *args, **kwargs):
        return [{'ident': parameter.ident,
                 'url': parameter.api_url()}
                for parameter in ParameterCache.objects.all()]


class AdapterChoiceView(View):
    """
    Choose your adapter instance.
    """
    def get(self, request, *args, **kwargs):
        return [{'name': fews_norm_source.name,
                 'url': fews_norm_source.api_url()}
                for fews_norm_source in FewsNormSource.objects.all()]


class AdapterView(View):
    """
    Class based REST view for adapter.
    """
    adapter = None  # This way your as_view kwargs will be passed

    def get(self, request, *args, **kwargs):
        parameter_id = request.GET.get('parameter_id', None)
        module_id = request.GET.get('module_id', None)
        fews_norm_source_slug = kwargs['fews_norm_source_slug']
        layer_arguments = {
            'parameter_id': parameter_id,
            'module_id': module_id,
            'fews_norm_source_slug': fews_norm_source_slug,
            }
        adapter_instance = self.adapter(None, layer_arguments=layer_arguments)
        return {'ja': 'ha'}
