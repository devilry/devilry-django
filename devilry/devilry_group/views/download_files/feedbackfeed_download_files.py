# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python imports

# django imports
from django import http
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic
from wsgiref.util import FileWrapper

# devilry imports
from django_cradmin import crapp
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_ziputil import backend_registry


class FileDownloadFeedbackfeedView(generic.View):
    """
    Download a single file uncompressed.
    """
    def get(self, request, commentfile_id):
        """Download a single file

        Args:
            request: The request object with a user.
            feedbackset_id: The FeedbackSet the files belong to.
            commentfile_id: The CommentFile to retreive the file from.

        Returns:
            HttpResponse: File.
        """
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


# class CompressedGroupCommentFileDownload(generic.View):
#     """Compress all files from a specific GroupComment into a zipped folder
#     """
#     def get(self, request, groupcomment_id):
#         """
#
#
#         Args:
#             groupcomment_id:
#             request:
#
#         Returns:
#              HttpResponse: Zipped folder.
#         """
#         groupcomment = get_object_or_404(group_models.GroupComment, id=groupcomment_id)
#
#         # Check that the cradmin role and the AssignmentGroup is the same.
#         if groupcomment.feedback_set.group.id != request.cradmin_role.id:
#             raise Http404()
#
#         # If it's a private GroupComment, the request.user must be the one that created the comment.
#         if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
#             raise Http404()
#
#         commentfiles = groupcomment.commentfile_set.all()
#
#         dirname = '{}-{}'.format(
#             groupcomment.user_role,
#             groupcomment.user
#         )
#
#         zip_file_name = '{}.zip'.format(dirname.encode('ascii', 'ignore'))
#         tempfile = NamedTemporaryFile()
#         zip_file = zipfile.ZipFile(tempfile, 'w')
#
#         for commentfile in commentfiles:
#             zip_file.write(
#                 commentfile.file.file.name,
#                 posixpath.join('', commentfile.filename)
#             )
#
#         zip_file.close()
#         tempfile.seek(0)
#
#         # Load file as chunks
#         filewrapper = FileWrapper(tempfile)
#         response = http.HttpResponse(filewrapper, content_type='application/zip')
#         response['content-disposition'] = 'attachment; filename=%s' % \
#             zip_file_name.encode('ascii', 'replace')
#         response['content-length'] = os.stat(tempfile.name).st_size
#         return response


class CompressedGroupCommentFileDownload(generic.View):
    """Compress all files from a specific GroupComment into a zipped folder
    """
    def get(self, request, groupcomment_id):
        """

        Args:
            groupcomment_id:
            request:

        Returns:
             HttpResponse: Zipped folder.
        """
        groupcomment = get_object_or_404(group_models.GroupComment, id=groupcomment_id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if groupcomment.feedback_set.group.id != request.cradmin_role.id:
            raise Http404()

        # If it's a private GroupComment, the request.user must be the one that created the comment.
        if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
            raise Http404()

        commentfiles = groupcomment.commentfile_set.all()

        archivename = '{}-{}.zip'.format(
            groupcomment.user_role,
            groupcomment.user
        )

        # Get backend and path
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
        zipfile_path = '{}/{}/{}/{}'.format(groupcomment.feedback_set.group.id,
                                            groupcomment.feedback_set.id,
                                            groupcomment.id,
                                            archivename)

        # Get backend instance
        zipfile_backend = zipfile_backend_class(
                archive_path=zipfile_path,
                readmode=False
        )

        # Write files to archive
        for commentfile in commentfiles:
            zipfile_backend.add_file('{}'.format(commentfile.filename), commentfile.file.file)
        zipfile_backend.close()

        # Add zipped archive to response
        zipfile_backend.readmode = True
        filewrapper = FileWrapper(zipfile_backend.read_archive())
        response = http.HttpResponse(filewrapper, content_type='application/zip')
        response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
        response['content-length'] = zipfile_backend.archive_size()
        return response


# class CompressedFeedbackSetFileDownloadView(generic.View):
#     """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.
#
#     Downloads only files from GroupComments that are visible to everyone.
#     """
#     def get(self, request, feedbackset_id):
#         """Download all files for a feedbackset into zipped folder.
#
#         Args:
#             request: The request object with a user.
#             feedbackset_id: The FeedbackSet the files belong to.
#
#         Returns:
#             HttpResponse: Zipped folder.
#         """
#         feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)
#
#         # Check that the cradmin role and the AssignmentGroup is the same.
#         if feedbackset.group.id != request.cradmin_role.id:
#             raise Http404()
#
#         dirname = '{}-{}-delivery'.format(
#             feedbackset.group.parentnode.get_path(),
#             feedbackset.group.short_displayname
#         )
#
#         zip_file_name = '{}.zip'.format(dirname.encode('ascii', 'ignore'))
#         tempfile = NamedTemporaryFile()
#         zip_file = zipfile.ZipFile(tempfile, 'w')
#
#         for group_comment in feedbackset.groupcomment_set.all():
#             # Don't add files from comments which are not visible to everyone.
#             if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
#                 for comment_file in group_comment.commentfile_set.all():
#                     if comment_file.comment.published_datetime > group_comment.feedback_set.deadline_datetime \
#                             and comment_file.comment.user_role == 'student':
#                         path = 'uploaded_after_deadline'
#                     elif comment_file.comment.user_role == 'examiner':
#                         path = 'uploaded_by_examiner'
#                     else:
#                         path = 'uploaded_by_student'
#                     zip_file.write(
#                             comment_file.file.file.name,
#                             posixpath.join(path, comment_file.filename)
#                         )
#
#         zip_file.close()
#         tempfile.seek(0)
#
#         # Load file as chunks rather than loading the whole file into memory
#         filewrapper = FileWrapper(tempfile)
#         response = http.HttpResponse(filewrapper, content_type='application/zip')
#         response['content-disposition'] = 'attachment; filename=%s' % \
#             zip_file_name.encode('ascii', 'replace')
#         response['content-length'] = os.stat(tempfile.name).st_size
#
#         return response

class CompressedFeedbackSetFileDownloadView(generic.View):
    """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.

    Downloads only files from GroupComments that are visible to everyone.
    """
    def get(self, request, feedbackset_id):
        """Download all files for a feedbackset into zipped folder.

        Args:
            request: The request object.
            feedbackset_id: The FeedbackSet the files belong to.

        Returns:
            HttpResponse: Response with zipped folder.
        """
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)

        # Check that the cradmin role and the AssignmentGroup is the same.
        if feedbackset.group.id != request.cradmin_role.id:
            raise Http404()

        archivename = '{}-{}-delivery.zip'.format(
            feedbackset.group.parentnode.get_path(),
            feedbackset.current_deadline()
        )

        # Get backend and path
        from devilry.devilry_ziputil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
        zipfile_path = '{}/{}/{}'.format(feedbackset.group.id,
                                         feedbackset.id,
                                         archivename)

        # Get backend instance
        zipfile_backend = zipfile_backend_class(
            archive_path=zipfile_path,
            readmode=False
        )

        # Write files to archive
        for group_comment in feedbackset.groupcomment_set.all():
            # Don't add files from comments which are not visible to everyone.
            if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
                for comment_file in group_comment.commentfile_set.all():
                    if comment_file.comment.user_role == 'student':
                        if comment_file.comment.published_datetime > feedbackset.current_deadline():
                            zipfile_backend.add_file('uploaded_after_deadline/{}'.format(comment_file.filename),
                                                     comment_file.file.file)
                        else:
                            zipfile_backend.add_file('delivery/{}'.format(comment_file.filename),
                                                     comment_file.file.file)
        zipfile_backend.close()

        # Add zipped archive to response
        zipfile_backend.readmode = True
        filewrapper = FileWrapper(zipfile_backend.read_archive())
        response = http.HttpResponse(filewrapper, content_type='application/zip')
        response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
        response['content-length'] = zipfile_backend.archive_size()

        return response


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
            FileDownloadFeedbackfeedView.as_view(),
            name='feedbackset-file-download'),
    ]
