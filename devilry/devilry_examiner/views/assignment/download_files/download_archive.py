# -*- coding: utf-8 -*-


from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic

from cradmin_legacy import crapp

from devilry.apps.core import models as core_models
from devilry.devilry_compressionutil import models as archivemodels
from devilry.devilry_examiner.views.assignment.download_files import batch_download_api
from devilry.utils.csrfutils import csrf_exempt_if_configured


class CompressedAssignmentFileDownloadView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id')
        assignment = get_object_or_404(core_models.Assignment, id=assignment_id)

        if assignment != self.request.cradmin_role:
            raise Http404()

        archive_meta = archivemodels.CompressedArchiveMeta.objects\
            .filter(content_object_id=assignment_id,
                    content_type=ContentType.objects.get_for_model(model=assignment),
                    deleted_datetime=None,
                    created_by=self.request.user,
                    created_by_role=archivemodels.CompressedArchiveMeta.CREATED_BY_ROLE_EXAMINER)\
            .order_by('-created_datetime').first()
        if not archive_meta:
            raise Http404()
        return archive_meta.make_download_httpresponse()


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^assignment-file-download/(?P<assignment_id>[0-9]+)$',
            CompressedAssignmentFileDownloadView.as_view(),
            name='assignment-file-download'),
        crapp.Url(
            r'assignment-download-api/(?P<content_object_id>[0-9]+)$',
            csrf_exempt_if_configured(batch_download_api.BatchCompressionAPIAssignmentView.as_view()),
            name='assignment-file-download-api'
        )
    ]
