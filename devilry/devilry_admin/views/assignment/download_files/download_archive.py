# -*- coding: utf-8 -*-
import os

from django.http import Http404
from django import http
from django.shortcuts import get_object_or_404
from django.views import generic

from cradmin_legacy import crapp

from devilry.apps.core import models as core_models
from devilry.devilry_admin.views.assignment.download_files import batch_download_api
from devilry.devilry_compressionutil import backend_registry
from devilry.devilry_compressionutil.batchjob_mixins.assignment_mixin import AssignmentBatchMixin


class CompressedAssignmentFileDownloadView(AssignmentBatchMixin, generic.TemplateView):
    backend_id = 'devilry_admin_local'

    def get_assignment_group_queryset(self, assignment, user):
        return assignment.assignmentgroups.filter_user_is_admin(user=user)

    def get(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id')
        assignment = get_object_or_404(core_models.Assignment, id=assignment_id)

        if assignment != self.request.cradmin_role:
            raise Http404()

        from django.utils import timezone
        archive_name = '{}.{}.{}.{}.zip'.format(
            assignment.subject.short_name,
            assignment.period.short_name,
            assignment.short_name,
            timezone.now().strftime('%Y-%m-%d-%H%M'))

        archive_path = os.path.join(
            'admin',
            str(assignment.parentnode.id),
            str(assignment.id),
            str(self.request.user),
            archive_name
        )

        zip_backend = backend_registry.Registry.get_backend_instance(
            backend_id=self.backend_id,
            zipfile_path=archive_path,
            archive_name=archive_name
        )

        if not zip_backend:
            raise Http404()

        self.add_assignment_groups(self.request.user, zip_backend, assignment)
        zip_backend.close()

        filewrapper = zip_backend.get_archive()
        content_type = 'application/octet-stream'

        response = http.StreamingHttpResponse(
            filewrapper,
            content_type=content_type
        )
        response['content-disposition'] = 'attachment; filename={}'.format(
            archive_name.encode('ascii', 'replace').decode()
        )
        if zip_backend.archive_size() > 0:
            response['content-length'] = zip_backend.archive_size()

        return response


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^assignment-file-download/(?P<assignment_id>[0-9]+)$',
            CompressedAssignmentFileDownloadView.as_view(),
            name='assignment-file-download'),
        crapp.Url(
            r'assignment-download-api/(?P<content_object_id>[0-9]+)$',
            batch_download_api.BatchCompressionAPIAssignmentView.as_view(),
            name='assignment-file-download-api'
        )
    ]
