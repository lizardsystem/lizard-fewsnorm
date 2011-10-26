from djangorestframework.resources import ModelResource

from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache


class LocationResource(ModelResource):
    """
    Locations
    """
    model = GeoLocationCache
    fields = ('name', 'fews_norm_source', 'shortname', 'parameter', 'module',)
    ordering = ('name', 'ident', )

    def parameter(self, instance):
        return [{'name': parameter.ident,
                 'url': parameter.api_url()}
                for parameter in instance.parameter.all()]


class ParameterResource(ModelResource):
    """
    Parameters
    """
    model = ParameterCache
    fields = ('ident', 'location')
    ordering = ('ident', )

    def location(self, instance):
        return [{'name': location.ident,
                 'url': location.api_url()}
                for location in instance.geolocationcache_set.all()]
