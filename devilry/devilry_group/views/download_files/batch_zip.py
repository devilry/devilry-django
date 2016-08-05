# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python imports
from tempfile import NamedTemporaryFile
import posixpath
import os
import zipfile
import time

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
from celery.task import task


@shared_task
def batch_zip_groupcomment(groupcomment):
    """

    Args:
        groupcomment:

    Returns:
         HttpResponse: Zipped folder.
    """
    # Fetch and mark batchoperation as running
    time.sleep(13)
    batchoperation = BatchOperation.objects.get(context_object_id=groupcomment.id)
    batchoperation.mark_as_running()

    commentfiles = groupcomment.commentfile_set.all()

    archivename = '{}-{}.zip'.format(
        groupcomment.user_role,
        groupcomment.user
    )

    # Get backend and path
    from devilry.devilry_ziputil import backend_registry
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
    zipfile_backend.close_archive()

    zipfile_backend.readmode = True
    filewrapper = FileWrapper(zipfile_backend.read_archive())
    response = http.HttpResponse(filewrapper, content_type='application/zip')
    response['content-disposition'] = 'attachment; filename=%s' % archivename.encode('ascii', 'replace')
    response['content-length'] = zipfile_backend.archive_size()
    batchoperation.finish(output_data=response)
