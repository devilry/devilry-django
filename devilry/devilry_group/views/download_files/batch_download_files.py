# -*- coding: utf-8 -*-
import re
from wsgiref.util import FileWrapper

from cradmin_legacy import crapp
from django import http
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic

from devilry.devilry_comment import models as comment_models
from devilry.devilry_compressionutil import models as archivemodels
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.download_files.batch_download_api import (
    BatchCompressionAPIFeedbackSetView,
)
from devilry.utils.csrfutils import csrf_exempt_if_configured


class FileDownloadFeedbackfeedView(generic.View):
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
        commentfile_id = kwargs.get("commentfile_id")
        comment_file = get_object_or_404(comment_models.CommentFile, id=commentfile_id)
        groupcomment = get_object_or_404(group_models.GroupComment, id=comment_file.comment.id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if groupcomment.feedback_set.group.id != request.cradmin_role.id:
            raise Http404()

        # Checks if comment is visible to user
        if not groupcomment.visible_to_user(request.user):
            raise Http404()

        return comment_file.make_download_httpresponse()


class CompressedFeedbackSetFileDownloadView(generic.TemplateView):
    """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.

    Downloads only files from GroupComments that are visible to everyone.
    """

    def get(self, request, *args, **kwargs):
        """Download all files for a feedbackset into zipped folder.

        Args:
            request (HttpRequest): Request from client.
        """
        feedbackset_id = kwargs.get("feedbackset_id")
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if feedbackset.group.id != request.cradmin_role.id:
            raise Http404()

        archive_meta = (
            archivemodels.CompressedArchiveMeta.objects.exclude()
            .filter(
                content_object_id=feedbackset_id,
                content_type=ContentType.objects.get_for_model(model=feedbackset),
                deleted_datetime=None,
            )
            .order_by("-created_datetime")
            .first()
        )
        if not archive_meta:
            raise Http404()
        return archive_meta.make_download_httpresponse()


class App(crapp.App):
    appurls = [
        crapp.Url(
            r"^file-download/(?P<commentfile_id>[0-9]+)$",
            FileDownloadFeedbackfeedView.as_view(),
            name="file-download",
        ),
        crapp.Url(
            r"^feedbackset-file-download/(?P<feedbackset_id>[0-9]+)$",
            CompressedFeedbackSetFileDownloadView.as_view(),
            name="feedbackset-file-download",
        ),
        crapp.Url(
            r"feedbackset-download-api/(?P<content_object_id>[0-9]+)$",
            csrf_exempt_if_configured(BatchCompressionAPIFeedbackSetView.as_view()),
            name="feedbackset-file-download-api",
        ),
    ]
