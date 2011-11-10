# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from lizard_map.views import AppView

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import ModuleInstances
from lizard_fewsnorm.models import Parameter


class HomepageView(AppView):
    template_name = 'lizard_fewsnorm/homepage.html'

    def fews_norm_sources(self):
        return FewsNormSource.objects.all()


class FewsNormSourceView(AppView):
    template_name = 'lizard_fewsnorm/fews_norm_source.html'

    def parameters(self):
        return self.fews_norm_source.o(Parameter).all()

    def modules(self):
        return self.fews_norm_source.o(ModuleInstances).all()

    def fews_norm_source(self):
        return self.fews_norm_source

    def get(self, request, *args, **kwargs):
        self.fews_norm_source = FewsNormSource.objects.get(
            slug=kwargs['fews_norm_source_slug'])
        return super(FewsNormSourceView, self).get(request, *args, **kwargs)
