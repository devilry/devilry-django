from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from devilry.devilry_extjsextras.views import DevilryExtjs4AppView


class AppView(DevilryExtjs4AppView):
    template_name = "devilry_nodeadmin/app.django.html"
    appname = 'devilry_nodeadmin'
    css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'


class RedirectToNodeAdminAppView(View):
    pathformat = None

    def get(self, request, **kwargs):
        path = self.pathformat.format(**kwargs)
        url = '{}?routeTo={}'.format(reverse('devilry_nodeadmin'), path)
        return HttpResponseRedirect(url)
