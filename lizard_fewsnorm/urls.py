# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
import lizard_fewsnorm.views

admin.autodiscover()

API_URL_NAME = 'lizard_fewsnorm_api_root'
NAME_PREFIX = 'lizard_fewsnorm_'

urlpatterns = patterns(
    '',
    url(r'^$',
        lizard_fewsnorm.views.HomepageView.as_view(),
        name=NAME_PREFIX+"homepage"),
    url(r'^source/(?P<fews_norm_source_slug>.*)/$',
        lizard_fewsnorm.views.FewsNormSourceView.as_view(),
        name=NAME_PREFIX+"source"),

    (r'^api/', include('lizard_fewsnorm.api.urls')),
    )
urlpatterns += debugmode_urlpatterns()
