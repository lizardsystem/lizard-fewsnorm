from djangorestframework.resources import ModelResource

from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache
from lizard_fewsnorm.models import FewsNormSource


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


class FewsNormSourceResource(ModelResource):
    """
    Fews norm source
    """
    model = FewsNormSource
    fields = ('name', 'slug', 'database_name', 'geo_location_cache', )
    ordering = ('name', )

    def geo_location_cache(self, instance):
        return [{'name': str(geo_location_cache),
                 'url': geo_location_cache.api_url()}
                for geo_location_cache in instance.geolocationcache_set.all()]
