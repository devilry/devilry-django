from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from django_cradmin import crapp
from ievv_opensource.ievv_batchframework.models import BatchOperation

from devilry.devilry_cradmin.viewhelpers.devilry_confirmview import View


class WaitForDownload(TemplateView):
    """
    Redirected to this view when downloading files.
    """
    template_name = 'devilry_group/wait_for_download.django.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        print pk
        return super(WaitForDownload, self).get(request=request, *args, **kwargs)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^wait-for-download//(?P<pk>\d+)$',
            WaitForDownload.as_view(),
            name='wait-for-download'
        )
    ]
