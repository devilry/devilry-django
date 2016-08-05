# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python imports
from tempfile import NamedTemporaryFile
import posixpath
import os
import zipfile

# django imports
from django import http
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.servers.basehttp import FileWrapper

# devilry imports
from django_cradmin import crapp

from devilry.devilry_group import models as group_models
from ievv_opensource.ievv_batchframework.models import BatchOperation
from celery import shared_task


# class CompressedGroupCommentFileDownload(generic.View):
#     """Compress all files from a specific GroupComment into a zipped folder
#     """
#     BatchOperation.objects.create_asyncronous(operation_type='zip-groupcomment')

@shared_task
def get_zipped_response(request, groupcomment_id):
    """

    Args:
        groupcomment_id:
        request:

    Returns:
         HttpResponse: Zipped folder.
    """
    # groupcomment = get_object_or_404(group_models.GroupComment, id=groupcomment_id)
    #
    # # Check that the cradmin role and the AssignmentGroup is the same.
    # if groupcomment.feedback_set.group.id != request.cradmin_role.id:
    #     raise Http404()
    #
    # # If it's a private GroupComment, the request.user must be the one that created the comment.
    # if groupcomment.visibility != group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
    #     raise Http404()
    #
    # commentfiles = groupcomment.commentfile_set.all()
    #
    # archivename = '{}-{}.zip'.format(
    #     groupcomment.user_role,
    #     groupcomment.user
    # )
    #
    # # Get backend and path
    # from devilry.devilry_ziputil import backend_registry
    # zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
    # zipfile_path = '{}/{}/{}/{}'.format(groupcomment.feedback_set.group.id,
    #                                     groupcomment.feedback_set.id,
    #                                     groupcomment.id,
    #                                     archivename)
    #
    # # Get backend instance
    # zipfile_backend = zipfile_backend_class(
    #         archive_path=zipfile_path,
    #         readmode=False
    # )
    #
    # # Write files to archive
    # for commentfile in commentfiles:
    #     zipfile_backend.add_file('{}'.format(commentfile.filename), commentfile.file.file)
    # zipfile_backend.close_archive()
    #
    # # Add zipped archive to response
    # zipfile_backend.readmode = True
    # filewrapper = FileWrapper(zipfile_backend.read_archive())
    # response = http.HttpResponse(filewrapper, content_type='application/zip')
    # response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
    # response['content-length'] = zipfile_backend.archive_size()
    # return response
    print groupcomment_id
    return 'done'
