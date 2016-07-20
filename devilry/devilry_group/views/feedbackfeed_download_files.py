# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python imports
from tempfile import NamedTemporaryFile
import posixpath
import os
import zipfile

# django imports
from django import http
from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.servers.basehttp import FileWrapper

# devilry imports
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models


class FileDownloadFeedbackfeedView(generic.View):
    """
    Download a single file uncompressed.
    """
    def get(self, request, feedbackset_id, commentfile_id):
        """Download a single file

        Args:
            request: The request object with a user.
            feedbackset_id: The FeedbackSet the files belong to.
            commentfile_id: The CommentFile to retreive the file from.

        Returns:
            HttpResponse with FileWrapper containing the file.
        """
        comment_file = get_object_or_404(comment_models.CommentFile, id=commentfile_id)

        # Load file as chunks rather than loading the whole file into memory
        filewrapper = FileWrapper(comment_file.file)
        response = http.HttpResponse(filewrapper, content_type=comment_file.mimetype)
        response['content-disposition'] = 'attachement; filename=%s' % \
            comment_file.filename.encode('ascii', 'replace')
        response['content-length'] = comment_file.filesize

        return response


class CompressedFeedbackSetFileDownloadView(generic.View):
    """
    Compress all files from a specific FeedbackSet for an assignment into a zip folder.
    """
    def get(self, request, feedbackset_id):
        """Download all files for a feedbackset into zipped folder.

        Args:
            request: The request object with a user.
            assignmentgroup_id: The FeedbackSet the files belong to.

        Returns:
            HttpResponse with FileWrapper containing the zipped folder.
        """
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)

        dirname = u'{}-{}-delivery'.format(
            feedbackset.group.parentnode.get_path(),
            feedbackset.group.short_displayname
        )

        zip_file_name = u'{}.zip'.format(dirname.encode('ascii', 'ignore'))
        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w')

        for group_comment in feedbackset.groupcomment_set.all():
            if group_comment.commentfile_set is not None:
                for comment_file in group_comment.commentfile_set.all():
                    if comment_file.comment.published_datetime > group_comment.feedback_set.deadline_datetime \
                            and comment_file.comment.user_role == u'student':
                        path = u'uploaded_after_deadline'
                    elif comment_file.comment.user_role == u'examiner':
                        path = u'uploaded_by_examiner'
                    else:
                        path = u'uploaded_by_student'
                    zip_file.write(
                            comment_file.file.file.name,
                            posixpath.join(path, comment_file.filename)
                        )

        zip_file.close()
        tempfile.seek(0)

        # Load file as chunks rather than loading the whole file into memory
        filewrapper = FileWrapper(tempfile.seek(0))
        response = http.HttpResponse(filewrapper, content_type='application/zip')
        response['content-disposition'] = 'attachement; filename=%s' % \
            zip_file_name.encode('ascii', 'replace')
        response['content-length'] = os.stat(tempfile.name).st_size

        return response
