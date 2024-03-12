# -*- coding: utf-8 -*-
from wsgiref.util import FileWrapper
import re
import os

from django import http
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from cradmin_legacy import crapp

from devilry.devilry_comment import models as comment_models
from devilry.devilry_compressionutil import models as archivemodels
from devilry.devilry_group import models as group_models
from devilry.devilry_group.utils import download_response
from devilry.devilry_group.views.download_files.batch_download_api import BatchCompressionAPIFeedbackSetView
from devilry.devilry_compressionutil.backend_registry import Registry
from devilry.devilry_compressionutil.batchjob_mixins.feedbackset_mixin import FeedbackSetBatchMixin




class FileDownloadFeedbackfeedView(generic.TemplateView):
    """
    Download a single file uncompressed.
    """
    def get(self, request, *args, **kwargs):
        """Download a single file

        Args:
            request: The request object with a user and :obj:`~devilry.devilry_comment.models.CommentFile.id`.

        Returns:
            HttpResponse: File.
        """
        commentfile_id = kwargs.get('commentfile_id')
        comment_file = get_object_or_404(comment_models.CommentFile, id=commentfile_id)
        groupcomment = get_object_or_404(group_models.GroupComment, id=comment_file.comment.id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if groupcomment.feedback_set.group.id != request.cradmin_role.id:
            raise Http404()

        # If it's a private GroupComment, the request.user must be the one that created the comment.
        if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
            if groupcomment.user != self.request.user:
                raise Http404()

        # Load file as chunks rather than loading the whole file into memory
        filewrapper = FileWrapper(comment_file.file)
        response = http.HttpResponse(filewrapper, content_type=comment_file.mimetype)
        filename = re.subn(r'[^a-zA-Z0-9._ -]', '', comment_file.filename.encode('ascii', 'replace').decode())[0]
        response['content-disposition'] = 'attachment; filename={}'.format(filename)
        response['content-length'] = comment_file.filesize

        return response


class CompressedFeedbackSetFileDownloadView(FeedbackSetBatchMixin, generic.TemplateView):
    """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.

    Downloads only files from GroupComments that are visible to everyone.
    """

    backend_id = 'devilry_group_local'

    def get(self, request, *args, **kwargs):
        """Download all files for a feedbackset into zipped folder.

        Args:
            request (HttpRequest): Request from client.

        Returns:
            Response: redirects to wait-for-download view,
                see :class:`~devilry.devilry_group.views.download_files.feedbackfeed_downloadviews.WaitForDownload`, or
                returns the content, see `~devilry.devilry_group.utils.download_response`.
        """
        feedbackset_id = kwargs.get('feedbackset_id')
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if feedbackset.group.id != request.cradmin_role.id:
            raise Http404()

        from django.utils import timezone
        archive_name = 'feedbackset-{}-{}-delivery.zip'.format(
            feedbackset.id,
            timezone.now().strftime('%Y-%m-%d-%H%M'))

        archive_path = os.path.join(
            str(feedbackset.group.parentnode.parentnode_id),
            str(feedbackset.group.parentnode.id),
            str(feedbackset.group.id),
            archive_name)

        zip_backend = Registry.get_backend_instance(
            backend_id=self.backend_id,
            zipfile_path=archive_path,
            archive_name=archive_name
        )
        if not zip_backend:
            raise Http404()

        self.zipfile_add_feedbackset(zipfile_backend=zip_backend, feedback_set=feedbackset)
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
            r'^file-download/(?P<commentfile_id>[0-9]+)$',
            FileDownloadFeedbackfeedView.as_view(),
            name='file-download'),
        crapp.Url(
            r'^feedbackset-file-download/(?P<feedbackset_id>[0-9]+)$',
            CompressedFeedbackSetFileDownloadView.as_view(),
            name='feedbackset-file-download'),
        crapp.Url(
            r'feedbackset-download-api/(?P<content_object_id>[0-9]+)$',
            BatchCompressionAPIFeedbackSetView.as_view(),
            name='feedbackset-file-download-api'
        )
    ]
