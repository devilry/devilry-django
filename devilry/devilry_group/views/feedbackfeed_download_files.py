import StringIO
import posixpath
from tempfile import NamedTemporaryFile
import os
import zipfile
from django import http
from django.shortcuts import get_object_or_404
from django.views import generic
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.apps.core import models as core_models


class FileDownloadFeedbackfeedView(generic.View):
    """

    """

    def get(self, request, feedbackset_id, commentfile_id):
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)
        comment_file = get_object_or_404(comment_models.CommentFile, id=commentfile_id)

        if not (feedbackset.group.is_candidate(request.user) \
                or feedbackset.group.is_examiner(request.user) \
                or feedbackset.group.is_admin(request.user)):
            return http.HttpResponseForbidden('Forbidden')

        response = http.HttpResponse(comment_file.file, content_type=comment_file.mimetype)
        response['content-disposition'] = 'attachement; filename=%s' % \
            comment_file.filename.encode('ascii', 'replace')
        response['content-length'] = comment_file.filesize

        return response

class CompressedFeedbackSetFileDownloadView(generic.View):
    """
    Compress all files from a specific FeedbackSet for an assignment into a zip folder.
    """
    def get(self, request, feedbackset_id):
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)

        if not (feedbackset.group.is_candidate(request.user) \
                or feedbackset.group.is_examiner(request.user) \
                or feedbackset.group.is_admin(request.user)):
            return http.HttpResponseForbidden('Forbidden')

        dirname = u'{}-{}-delivery-{}'.format(
            feedbackset.group.parentnode.get_path(),
            feedbackset.group.short_displayname,
            feedbackset.group.id
        )

        zip_file_name = u'{}.zip'.format(dirname.encode('ascii', 'ignore'))

        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for group_comment in feedbackset.groupcomment_set.all():
            if not (group_comment.commentfile_set is None):
                for comment_file in group_comment.commentfile_set.all():
                    zip_file.write(comment_file.file.file.name, posixpath.join(dirname, comment_file.filename))

        zip_file.close()

        tempfile.seek(0)
        response = http.HttpResponse(tempfile, content_type=comment_file.mimetype)
        response['content-disposition'] = 'attachement; filename=%s' % \
            zip_file_name.encode('ascii', 'replace')
        response['content-length'] = os.stat(tempfile.name).st_size

        return response

class CompressedAllFeedbackSetsFileDownloadView(generic.View):
    """
    Compress all files from all feedbacksets for an assignment.
    """
    def get(self, request, feedbackset_id):
        feedbackset = get_object_or_404(group_models.FeedbackSet, id=feedbackset_id)
        assignmentgroup = get_object_or_404(core_models.AssignmentGroup, id=feedbackset.group.id)

        if not (assignmentgroup.is_candidate(request.user) \
                or assignmentgroup.is_examiner(request.user) \
                or assignmentgroup.is_admin(request.user)):
            return http.HttpResponseForbidden('Forbidden')

        dirname = u'{}-{}-delivery{}'.format(
            assignmentgroup.parentnode.get_path(),
            assignmentgroup.short_displayname,
            assignmentgroup.id
        )

        zip_file_name = u'{}.zip'.format(dirname.encode('ascii', 'ignore'))

        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w')

        for feedbackset in assignmentgroup.feedbackset_set.all():
            for group_comment in feedbackset.groupcomment_set.all():
                if not (group_comment.commentfile_set is None):
                    for comment_file in group_comment.commentfile_set.all():
                        zip_file.write(comment_file.file.file.name, posixpath.join(dirname, comment_file.filename))

        zip_file.close()

        tempfile.seek(0)
        response = http.HttpResponse(tempfile, content_type=comment_file.mimetype)
        response['content-disposition'] = 'attachement; filename=%s' % \
            zip_file_name.encode('ascii', 'replace')
        response['content-length'] = os.stat(tempfile.name).st_size

        return response

