from django.contrib.gis import admin

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ModuleCache
from lizard_fewsnorm.models import ParameterCache
from lizard_fewsnorm.models import QualifierSetCache
from lizard_fewsnorm.models import TimeStepCache
from lizard_fewsnorm.models import TimeSeriesCache
from lizard_fewsnorm.models import TrackRecordCache


class FewsNormSourceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class TimeSeriesCacheAdmin(admin.ModelAdmin):
    list_filter = ('active', 'geolocationcache',
                   'parametercache', 'modulecache', 'timestepcache', )
    list_display = ('__unicode__', 'active', 'geolocationcache',
                    'parametercache', 'modulecache', 'timestepcache', )


class GeoLocationCacheAdmin(admin.ModelAdmin):
    list_filter = ('active', 'data_set', 'fews_norm_source',
                   'parameter', 'module', 'timestep', )


admin.site.register(FewsNormSource, FewsNormSourceAdmin)
admin.site.register(GeoLocationCache, GeoLocationCacheAdmin)
admin.site.register(ModuleCache)
admin.site.register(ParameterCache)
admin.site.register(QualifierSetCache)
admin.site.register(TimeStepCache)
admin.site.register(TrackRecordCache)
admin.site.register(TimeSeriesCache, TimeSeriesCacheAdmin)
