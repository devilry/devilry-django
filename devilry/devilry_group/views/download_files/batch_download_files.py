# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from wsgiref.util import FileWrapper

from django import http
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from django_cradmin import crapp

from devilry.devilry_comment import models as comment_models
from devilry.devilry_compressionutil import models as archivemodels
from devilry.devilry_group import models as group_models
from devilry.devilry_group.utils import download_response
from devilry.devilry_group.views.download_files.batch_download_api import BatchCompressionAPIFeedbackSetView


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
        response['content-disposition'] = 'attachment; filename=%s' % \
            comment_file.filename.encode('ascii', 'replace')
        response['content-length'] = comment_file.filesize

        return response


class CompressedFeedbackSetFileDownloadView(generic.TemplateView):
    """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.

    Downloads only files from GroupComments that are visible to everyone.
    """
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

        archive_meta = archivemodels.CompressedArchiveMeta.objects.exclude()\
            .filter(content_object_id=feedbackset_id,
                    content_type=ContentType.objects.get_for_model(model=feedbackset),
                    deleted_datetime=None)\
            .order_by('-created_datetime').first()
        return download_response.download_response(
                content_path=archive_meta.archive_path,
                content_name=archive_meta.archive_name,
                content_type='application/zip',
                content_size=archive_meta.archive_size,
                streaming_response=True)


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
