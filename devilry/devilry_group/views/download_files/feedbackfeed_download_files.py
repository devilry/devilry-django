# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
#
# # python imports
#
# # django imports
# import os
#
# from django import http
# from django.http import Http404
# from django.shortcuts import get_object_or_404
# from django.views import generic
# from wsgiref.util import FileWrapper
#
# # devilry imports
# from django_cradmin import crapp
# from devilry.devilry_group import models as group_models
# from devilry.devilry_comment import models as comment_models
# from devilry.devilry_compressionutil import backend_registry
#
#
# class FileDownloadFeedbackfeedView(generic.View):
#     """
#     Download a single file uncompressed.
#     """
#     def get(self, request, commentfile_id):
#         """Download a single file
#
#         Args:
#             request: The request object with a user.
#             feedbackset_id: The FeedbackSet the files belong to.
#             commentfile_id: The CommentFile to retreive the file from.
#
#         Returns:
#             HttpResponse: File.
#         """
#         comment_file = get_object_or_404(comment_models.CommentFile, id=commentfile_id)
#         groupcomment = get_object_or_404(group_models.GroupComment, id=comment_file.comment.id)
#
#         # Check that the cradmin role and the AssignmentGroup is the same.
#         if groupcomment.feedback_set.group.id != request.cradmin_role.id:
#             raise Http404()
#
#         # If it's a private GroupComment, the request.user must be the one that created the comment.
#         if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
#             raise Http404()
#
#         # Load file as chunks rather than loading the whole file into memory
#         filewrapper = FileWrapper(comment_file.file)
#         response = http.HttpResponse(filewrapper, content_type=comment_file.mimetype)
#         response['content-disposition'] = 'attachment; filename=%s' % \
#             comment_file.filename.encode('ascii', 'replace')
#         response['content-length'] = comment_file.filesize
#
#         return response
#
#
# class CompressedGroupCommentFileDownload(generic.View):
#     """Compress all files from a specific GroupComment into a zipped folder
#     """
#     def get(self, request, groupcomment_id):
#         """
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
#         archivename = '{}-{}.zip'.format(
#             groupcomment.user_role,
#             groupcomment.user
#         )
#
#         # Get backend and path
#         zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
#         zipfile_path = os.path.join('%d' % groupcomment.feedback_set.group.id,
#                                     '%d' % groupcomment.feedback_set.id,
#                                     '%d' % groupcomment.id,
#                                     archivename)
#
#         # Get backend instance
#         zipfile_backend = zipfile_backend_class(
#                 archive_path=zipfile_path,
#                 archive_name=archivename,
#                 readmode=False
#         )
#
#         # Write files to archive
#         for commentfile in commentfiles:
#             zipfile_backend.add_file('{}'.format(commentfile.filename), commentfile.file.file)
#         zipfile_backend.close()
#
#         # Add zipped archive to response
#         zipfile_backend.readmode = True
#         filewrapper = FileWrapper(zipfile_backend.read_binary())
#         response = http.HttpResponse(filewrapper, content_type='application/zip')
#         response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
#         response['content-length'] = zipfile_backend.archive_size()
#         return response
#
#
# class CompressedFeedbackSetFileDownloadView(generic.View):
#     """Compress all files from a specific FeedbackSet for an assignment into a zipped folder.
#
#     Downloads only files from GroupComments that are visible to everyone.
#     """
#     def get(self, request, feedbackset_id):
#         """Download all files for a feedbackset into zipped folder.
#
#         Args:
#             request: The request object.
#             feedbackset_id: The FeedbackSet the files belong to.
#
#         Returns:
#             HttpResponse: Response with zipped folder.
#         """
#         feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)
#
#         # Check that the cradmin role and the AssignmentGroup is the same.
#         if feedbackset.group.id != request.cradmin_role.id:
#             raise Http404()
#
#         archivename = '{}-{}-delivery.zip'.format(
#             feedbackset.group.parentnode.get_path(),
#             feedbackset.current_deadline()
#         )
#
#         # Get backend and path
#         from devilry.devilry_compressionutil import backend_registry
#         zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
#         zipfile_path = os.path.join('%d' % feedbackset.group.id,
#                                     '%d' % feedbackset.id,
#                                     archivename)
#
#         # Get backend instance
#         zipfile_backend = zipfile_backend_class(
#             archive_path=zipfile_path,
#             archive_name=archivename,
#             readmode=False
#         )
#
#         # Write files to archive
#         for group_comment in feedbackset.groupcomment_set.all():
#             # Don't add files from comments which are not visible to everyone.
#             if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
#                 for comment_file in group_comment.commentfile_set.all():
#                     if comment_file.comment.user_role == 'student':
#                         if comment_file.comment.published_datetime > feedbackset.current_deadline():
#                             zipfile_backend.add_file(os.path.join('uploaded_after_deadline', comment_file.filename),
#                                                      comment_file.file.file)
#                         else:
#                             zipfile_backend.add_file(os.path.join('delivery', comment_file.filename),
#                                                      comment_file.file.file)
#         zipfile_backend.close()
#
#         # Add zipped archive to response
#         zipfile_backend.readmode = True
#         filewrapper = FileWrapper(zipfile_backend.read_binary())
#         response = http.HttpResponse(filewrapper, content_type='application/zip')
#         response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
#         response['content-length'] = zipfile_backend.archive_size()
#
#         return response
#
#
# class App(crapp.App):
#     appurls = [
#         crapp.Url(
#             r'^file-download/(?P<commentfile_id>[0-9]+)$',
#             FileDownloadFeedbackfeedView.as_view(),
#             name='file-download'),
#         crapp.Url(
#             r'^groupcomment-file-download/(?P<groupcomment_id>[0-9]+)$',
#             CompressedGroupCommentFileDownload.as_view(),
#             name='groupcomment-file-download'),
#         crapp.Url(
#             r'^feedbackset-file-download/(?P<feedbackset_id>[0-9]+)$',
#             FileDownloadFeedbackfeedView.as_view(),
#             name='feedbackset-file-download'),
#     ]
