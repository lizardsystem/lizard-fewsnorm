# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from django.contrib import admin

from lizard_fewsnorm.api.views import AdapterView
from lizard_fewsnorm.layers import AdapterFewsNorm


admin.autodiscover()

NAME_PREFIX = 'lizard_fewsnorm_api_'

urlpatterns = patterns(
    '',
    url(r'^$',
        AdapterView.as_view(resource=AdapterFewsNorm),
        name=NAME_PREFIX + 'root'),
    )
