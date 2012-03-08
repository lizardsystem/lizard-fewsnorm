from django.contrib.gis import admin

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache
from lizard_fewsnorm.models import ModuleCache
from lizard_fewsnorm.models import ParameterCache
from lizard_fewsnorm.models import QualifierSetCache
from lizard_fewsnorm.models import TimeStepCache
from lizard_fewsnorm.models import TimeSeriesCache
from lizard_fewsnorm.models import TrackRecordCache

# These models don't come from the default database.
# from lizard_fewsnorm.models import Users
# from lizard_fewsnorm.models import ParameterGroups
# from lizard_fewsnorm.models import Locations
# from lizard_fewsnorm.models import Parameters
# from lizard_fewsnorm.models import Qualifiers
# from lizard_fewsnorm.models import QualifierSets
# from lizard_fewsnorm.models import ModuleInstances
# from lizard_fewsnorm.models import Timesteps
# from lizard_fewsnorm.models import AggregationPeriods
# from lizard_fewsnorm.models import TimeseriesKeys
# from lizard_fewsnorm.models import TimeseriesValuesAndFlags
# from lizard_fewsnorm.models import TimeseriesComments
# from lizard_fewsnorm.models import TimeseriesManualEditsHistory


class FewsNormSourceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class TimeSeriesCacheAdmin(admin.ModelAdmin):
    list_filter = ('active', 'geolocationcache',
                   'parametercache', 'modulecache', 'timestepcache', )
    list_display = ('__unicode__', 'active', 'geolocationcache',
                    'parametercache', 'modulecache', 'timestepcache', )


class GeoLocationCacheAdmin(admin.ModelAdmin):
    list_filter = ('active', )


admin.site.register(FewsNormSource, FewsNormSourceAdmin)
admin.site.register(GeoLocationCache, GeoLocationCacheAdmin)
admin.site.register(ModuleCache)
admin.site.register(ParameterCache)
admin.site.register(QualifierSetCache)
admin.site.register(TimeStepCache)
admin.site.register(TrackRecordCache)
admin.site.register(TimeSeriesCache, TimeSeriesCacheAdmin)
