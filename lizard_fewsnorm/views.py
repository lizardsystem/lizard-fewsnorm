# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from lizard_map.views import AppView

from lizard_fewsnorm.models import FewsNormSource
# from lizard_fewsnorm.models import ModuleInstances
# from lizard_fewsnorm.models import Parameter
from lizard_fewsnorm.models import TimeSeriesCache


class HomepageView(AppView):
    template_name = 'lizard_fewsnorm/homepage.html'

    def fews_norm_sources(self):
        return FewsNormSource.objects.all()


class FewsNormSourceView(AppView):
    template_name = 'lizard_fewsnorm/fews_norm_source.html'
    fews_norm_source = None

    def source_parameter_modules(self):
        """
        Return unique parameter - module combinations that are in
        TimeSeriesCache.
        """

        spm = TimeSeriesCache.objects.filter(
            geolocationcache__fews_norm_source=self.fews_norm_source).values(
            'geolocationcache__fews_norm_source__name',
            'geolocationcache__fews_norm_source__slug',
            'parametercache__ident', 'modulecache__ident').distinct()
        return spm

    def get(self, request, *args, **kwargs):
        self.fews_norm_source = FewsNormSource.objects.get(
            slug=kwargs['fews_norm_source_slug'])
        return super(FewsNormSourceView, self).get(request, *args, **kwargs)
