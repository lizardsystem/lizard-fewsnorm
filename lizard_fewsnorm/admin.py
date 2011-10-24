from django.contrib.gis import admin

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoLocationCache


admin.site.register(FewsNormSource)
admin.site.register(GeoLocationCache)
