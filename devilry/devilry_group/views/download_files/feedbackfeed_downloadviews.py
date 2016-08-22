from wsgiref.util import FileWrapper

# Django imports
from django import http
from django.views.generic import TemplateView
from django_cradmin import crapp

# Devilry imports
from devilry.devilry_ziputil import models as zipmodels
from devilry.devilry_group.utils import download_response


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
        object_id = int(self.kwargs.get('pk'))
        archive_meta = zipmodels.CompressedArchiveMeta.objects.get(content_object_id=object_id)
        if archive_meta is not None:
            self.status = 'FINISHED'
            return download_response.download_response(
                    content_path=archive_meta.archive_path,
                    content_name=archive_meta.archive_name,
                    content_type='application/zip',
                    content_size=archive_meta.archive_size
            )
        return super(WaitForDownload, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WaitForDownload, self).get_context_data(**kwargs)
        context['status'] = self.status
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^wait-for-download/(?P<pk>[0-9]+)$',
            WaitForDownload.as_view(),
            name='wait-for-download'
        )
    ]
