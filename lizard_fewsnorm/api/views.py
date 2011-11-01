from djangorestframework.views import View
from django.core.urlresolvers import reverse

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache

from lizard_fewsnorm.layers import AdapterFewsNorm
from lizard_map.adapter import adapter_serialize

class RootView(View):
    """
    Class based REST root view.
    """
    def get(self, request):
        return {
            # 'adapter': {
            #     'name': 'adapter-fewsnorm',
            #     'url': reverse("lizard_fewsnorm_api_adapter_choice")},
            'identifier': {
                'name': 'identifier',
                'url': reverse("lizard_fewsnorm_api_identifier")},
            'source': {
                'name': 'source',
                'url': reverse("lizard_fewsnorm_api_source_list")},
            'location': {
                'name': 'location',
                'url': reverse("lizard_fewsnorm_api_location")},
            'parameter': {
                'name': 'parameter',
                'url': reverse("lizard_fewsnorm_api_parameter")}
            }

class IdentifierView(View):
    """
    Identifier
    """
    def get(self, request, *args, **kwargs):
        img_url = reverse(
            'lizard_map_adapter_image',
            kwargs={'adapter_class': 'adapter_fewsnorm'})
        values_csv_url = reverse(
            'lizard_map_adapter_values',
            kwargs={'adapter_class': 'adapter_fewsnorm',
                    'output_type': 'csv'})
        values_html_url = reverse(
            'lizard_map_adapter_values',
            kwargs={'adapter_class': 'adapter_fewsnorm',
                    'output_type': 'html'})

        result = []
        for identifier in AdapterFewsNorm.identifiers():
            serialized_identifier = adapter_serialize(identifier)
            img_url_id = '%s?identifier=%s' % (img_url, serialized_identifier)
            values_csv_url_id = '%s?identifier=%s' % (
                values_csv_url, serialized_identifier)
            values_html_url_id = '%s?identifier=%s' % (
                values_html_url, serialized_identifier)
            result.append({
                    'identifier': serialized_identifier,
                    'img_url': img_url_id,
                    'values_csv_url': values_csv_url_id,
                    'values_html_url': values_html_url_id,})
        return result


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
        """
        Execute adapter function.

        If adapter_function is in get kwargs, it will try to execute
        the adapter_function with named parameters from request.GET.
        """
        fews_norm_source_slug = kwargs['fews_norm_source_slug']
        parameter_id = request.GET.get('parameter_id', None)
        module_id = request.GET.get('module_id', None)
        layer_arguments = {
            'parameter_id': parameter_id,
            'module_id': module_id,
            'fews_norm_source_slug': fews_norm_source_slug,
            }
        if 'adapter_function' in kwargs:
            adapter_instance = self.adapter(
                None, layer_arguments=layer_arguments)
            adapter_function = kwargs['adapter_function']
            # Experimental: Execute
            adapter_args = {}
            return getattr(adapter_instance, adapter_function)(**adapter_args)
        else:
            return {'attributes': dir(self.adapter)}
