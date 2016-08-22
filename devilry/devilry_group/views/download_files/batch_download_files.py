# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# django imports
from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from wsgiref.util import FileWrapper

# ievv_opensource imports
from ievv_opensource.ievv_batchframework import batchregistry

# devilry imports
from django_cradmin import crapp
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_ziputil import models as zipmodels
from devilry.devilry_group.utils import download_response


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
            raise Http404()

        # Load file as chunks rather than loading the whole file into memory
        filewrapper = FileWrapper(comment_file.file)
        response = http.HttpResponse(filewrapper, content_type=comment_file.mimetype)
        response['content-disposition'] = 'attachment; filename=%s' % \
            comment_file.filename.encode('ascii', 'replace')
        response['content-length'] = comment_file.filesize

        return response


class CompressedGroupCommentFileDownload(generic.TemplateView):
    """Compress all files from a specific GroupComment into a zipped folder
    """

    def get(self, request, *args, **kwargs):
        """
        Checks permission

        Args:
            request (HttpRequest): Request from client.

        Returns:
            Response: redirects to wait-for-download view,
                see :class:`~devilry.devilry_group.views.download_files.feedbackfeed_downloadviews.WaitForDownload`, or
                returns the content, see `~devilry.devilry_group.utils.download_response`.
        """
        groupcomment_id = kwargs.get('groupcomment_id')
        groupcomment = get_object_or_404(group_models.GroupComment, id=groupcomment_id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if groupcomment.feedback_set.group.id != request.cradmin_role.id:
            raise Http404()

        # If it's a private GroupComment, the request.user must be the one that created the comment.
        if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
            raise Http404()

        # Check if archive exists
        try:
            archive_meta = zipmodels.CompressedArchiveMeta.objects.get(content_object_id=groupcomment_id)
        except ObjectDoesNotExist:
            # Run actiongroup.
            batchregistry.Registry.get_instance().run(
                actiongroup_name='batchframework_compress_groupcomment',
                context_object=groupcomment,
            )
        else:
            # Send response.
            return download_response.download_response(
                    content_path=archive_meta.get_full_path(),
                    content_name=archive_meta.archive_path,
                    content_type='application/zip',
                    content_size=archive_meta.archive_size
            )

        return HttpResponseRedirect(
                self.request.cradmin_app.reverse_appurl('wait-for-download', groupcomment_id))


class CompressedFeedbackSetFileDownloadView(generic.TemplateView):
    """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.

    Downloads only files from GroupComments that are visible to everyone.
    """
    def get(self, request, *args, **kwargs):
        """Download all files for a feedbackset into zipped folder.

        Args:
            request (HttpRequest): Request from client..

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

        # Check if archive exists
        try:
            archive_meta = zipmodels.CompressedArchiveMeta.objects.get(content_object_id=feedbackset_id)
        except ObjectDoesNotExist:
            # Run actiongroup
            batchregistry.Registry.get_instance().run(
                actiongroup_name='batchframework_compress_feedbackset',
                context_object=feedbackset,
            )
        else:
            # Send response
            return download_response.download_response(
                    content_path=archive_meta.get_full_path(),
                    content_name=archive_meta.archive_path,
                    content_type='application/zip',
                    content_size=archive_meta.archive_size
            )

        return HttpResponseRedirect(
                self.request.cradmin_app.reverse_appurl('wait-for-download', feedbackset_id))


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^file-download/(?P<commentfile_id>[0-9]+)$',
            FileDownloadFeedbackfeedView.as_view(),
            name='file-download'),
        crapp.Url(
            r'^groupcomment-file-download/(?P<groupcomment_id>[0-9]+)$',
            CompressedGroupCommentFileDownload.as_view(),
            name='groupcomment-file-download'),
        crapp.Url(
            r'^feedbackset-file-download/(?P<feedbackset_id>[0-9]+)$',
            CompressedFeedbackSetFileDownloadView.as_view(),
            name='feedbackset-file-download'),
    ]
