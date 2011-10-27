# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from djangorestframework.views import InstanceModelView
from djangorestframework.views import ListOrCreateModelView

from lizard_fewsnorm.api.resources import LocationResource
from lizard_fewsnorm.api.resources import ParameterResource
from lizard_fewsnorm.api.resources import FewsNormSourceResource

from lizard_fewsnorm.api.views import AdapterView
from lizard_fewsnorm.api.views import AdapterChoiceView
from lizard_fewsnorm.api.views import RootView
from lizard_fewsnorm.layers import AdapterFewsNorm
from lizard_fewsnorm.api.views import ParameterView
from lizard_fewsnorm.api.views import LocationView


admin.autodiscover()

NAME_PREFIX = 'lizard_fewsnorm_api_'

urlpatterns = patterns(
    '',
    url(r'^$',
        RootView.as_view(),
        name=NAME_PREFIX + 'root'),
    url(r'^source/$',
        ListOrCreateModelView.as_view(resource=FewsNormSourceResource),
        name=NAME_PREFIX + 'source_list'),
    url(r'^source/(?P<slug>.*)/$',
        InstanceModelView.as_view(resource=FewsNormSourceResource),
        name=NAME_PREFIX + 'source_detail'),
    url(r'^location/$',
        LocationView.as_view(),
        name=NAME_PREFIX + 'location'),
    url(r'^location/(?P<ident>.*)/$',
        InstanceModelView.as_view(resource=LocationResource),
        name=NAME_PREFIX + 'location_detail'),
    url(r'^parameter/$',
        ParameterView.as_view(),
        name=NAME_PREFIX + 'parameter'),
    url(r'^parameter/(?P<ident>.*)/$',
        InstanceModelView.as_view(resource=ParameterResource),
        name=NAME_PREFIX + 'parameter_detail'),
    url(r'^adapter/$',
        AdapterChoiceView.as_view(),
        name=NAME_PREFIX + 'adapter_choice'),
    url(r'^adapter/(?P<fews_norm_source_slug>[-\w]+)/$',
        AdapterView.as_view(adapter=AdapterFewsNorm),
        name=NAME_PREFIX + 'adapter'),
    url(r'^adapter/(?P<fews_norm_source_slug>[-\w]+)/(?P<adapter_function>.*)/$',
        AdapterView.as_view(adapter=AdapterFewsNorm),
        name=NAME_PREFIX + 'adapter'),
    )
