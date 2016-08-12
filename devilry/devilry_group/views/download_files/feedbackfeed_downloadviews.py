# Django imports
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django_cradmin import crapp

# ievv_opensource imports
from ievv_opensource.ievv_batchframework.models import BatchOperation

from devilry.devilry_group.models import GroupComment


class WaitForDownload(TemplateView):
    """
    Redirected to this view when downloading files.
    """
    template_name = 'devilry_group/wait_for_download.django.html'

    def __init__(self):
        super(WaitForDownload, self).__init__()
        self.status = 'NOT FINISHED'

    def get(self, request, *args, **kwargs):
        """
        """
        batchoperation_id = self.kwargs.get('pk')
        print batchoperation_id

        return super(WaitForDownload, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WaitForDownload, self).get_context_data(**kwargs)
        context['status'] = self.status
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^wait-for-download/(\d+)$',
            WaitForDownload.as_view(),
            name='wait-for-download'
        )
    ]
