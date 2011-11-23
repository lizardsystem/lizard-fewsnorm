from djangorestframework.resources import ModelResource

from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ParameterCache
from lizard_fewsnorm.models import TimeSeriesCache
from lizard_fewsnorm.models import FewsNormSource

from lizard_fewsnorm.models import Series


class LocationResource(ModelResource):
    """
    Locations
    """
    model = GeoLocationCache
    fields = ('name', 'fews_norm_source', 'shortname', 'parameter', 'module',
              'timeseries')
    ordering = ('name', 'ident', )

    def parameter(self, instance):
        return [{'name': parameter.ident,
                 'url': parameter.api_url()}
                for parameter in instance.parameter.all().distinct()]

    def module(self, instance):
        return [{'name': module.ident,
                 'id': module.id}
                for module in instance.module.all().distinct()]

    def timeseries(self, instance):
        return [{'name': str(ts),
                 'url': ts.api_url(),
                }
                for ts in instance.timeseriescache_set.all().distinct()]


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


class TimeSeriesResource(ModelResource):
    """
    Time Series with events.
    """
    model = TimeSeriesCache
    fields = ('location', 'module', 'parameter', 'timestep', 'events', )

    def location(self, instance):
        return [{'name': str(instance.geolocationcache),
                 'url': instance.geolocationcache.api_url()}]

    def module(self, instance):
        return [{'name': str(instance.modulecache),
                 'id': instance.modulecache.id}]

    def parameter(self, instance):
        return [{'name': str(instance.parametercache),
                 'url': instance.parametercache.api_url()}]

    def timestep(self, instance):
        return [{'name': str(instance.timestepcache),
                 'id': instance.timestepcache.id}]

    def events(self, instance):
        db_name = instance.geolocationcache.fews_norm_source.database_name
        series = Series.objects.using(db_name).get(
            location__id=instance.geolocationcache.ident,
            parameter__id=instance.parametercache.ident,
            moduleinstance__id=instance.modulecache.ident)
        return [{'timestamp': event.timestamp,
                 'value': event.value,
                 'flag': event.flag,
                 'comment': event.comment}
                for event in series.event_set.all()]
