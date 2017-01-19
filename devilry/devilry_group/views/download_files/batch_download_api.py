# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http.response import JsonResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404

from ievv_opensource.ievv_batchframework.models import BatchOperation
from ievv_opensource.ievv_batchframework import batchregistry

from devilry.devilry_compressionutil import models as compression_models
from devilry.devilry_group import models as group_models


class AbstractBatchCompressionAPIView(View):
    """
    Defines API for checking the status of compressed archives.

    Returns a JsonReponse containing the status for the batchoperations that compresses archives for download,
    whether the batchoperation is not created all, created but not started, running and finished.

    Examples:
        Below are the different JSON-responses returned from subclasses of this view from GET.
        If the subclasses adds more stuff, this should be documented there::

            If the BatchOperation is NOT created::
                '{"status": "not-created"}'

            If the BatchOperation IS created, but not started::
                '{"status": "not-started"}'

            If the BatchOperation is running::
                '{"status": "running"}'

            If the BatchOperation is finished(CompressedArchiveMeta exists)::
                '{"status": "finished", "download_link": "some download link"}'
    """
    def _compressed_archive_created(self, content_object_id):
        """
        Check if an entry of :class:`~.devilry.devilry_compressionutil.models.CompressedArchiveMeta` exists.

        Args:
            content_object_id: the object referred to.

        Returns:
            (:class:`~.devilry.devilry_compressionutil.models.CompressedArchiveMeta`): instance or ``None``.
        """
        try:
            archive_meta = compression_models.CompressedArchiveMeta.objects.get(content_object_id=content_object_id)
        except compression_models.CompressedArchiveMeta.DoesNotExist:
            return None
        return archive_meta

    def get_status_dict(self, context_object_id):
        """
        Checks if there exists a ``BatchOperation`` for the requested object.

        Checks the status of the ``BatchOperation`` for the requested object and builds a
        JSON-serializable dictionary with the response.

        Args:
            context_object_id: object the BatchOperation references.

        Returns:
            (dict): A JSON-serializable dictionary.
        """
        try:
            batchoperation = BatchOperation.objects.get(context_object_id=context_object_id)
        except BatchOperation.DoesNotExist:
            return {'status': 'not-created'}

        # The ``BatchOperation`` exists. Check the status.
        status = batchoperation.status
        if status == BatchOperation.STATUS_UNPROCESSED:
            return {'status': 'not-started'}
        return {'status': 'running'}

    def get_ready_for_download_status(self, content_object_id=None):
        """
        Override this to add the url for the download view.

        Ovrerride by adding a call to super and then add the download link to the
        entry ``download_link`` in the dictionary.
        
        Examples:
            Adding the downloadlink in subclass::

                def get_ready_for_download(self, content_object_id):
                    status_dict = super(BatchCompressionAPIGroupCommentView, self).get_ready_for_download_status()
                    status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
                        viewname='groupcomment-file-download',
                        kwargs={
                            'groupcomment_id': content_object_id
                        })
                    return status_dict
        
        Args:
            content_object_id (int): id of the object we use as url argument for the downloadview.

        Returns:
            (dict): A dictionary with the entries ``status`` and ``download_link``
        """
        return {'status': 'finished', 'download_link': content_object_id}

    def get_response_status(self, content_object_id):
        """
        Get the built response message as a dictionary.

        Args:
            content_object_id (int): id of the object from url argument.

        Returns:
            (dict): a JSON-serializable dictionary.
        """
        if self._compressed_archive_created(content_object_id=content_object_id):
            return self.get_ready_for_download_status(content_object_id=content_object_id)
        return self.get_status_dict(context_object_id=content_object_id)

    def start_compression_task(self, content_object_id):
        """
        Start the compression task. This function is used by POST.

        This must be implemented by a subclass that starts the

        Args:
            content_object_id: Id of the object we want to compress.

        Returns:

        """
        raise NotImplementedError('must be implemented by subclass')

    def get(self, request, *args, **kwargs):
        """
        Expects a id of the element to download as url argument with name ``content_object_id``.

        Returns:
            (JsonResponse): Status of the compression.
        """
        return JsonResponse(self.get_response_status(content_object_id=kwargs.get('content_object_id')))

    def post(self, request, *args, **kwargs):
        """
        Returns:
            (JsonResponse): Status of the compression.
        """
        content_object_id = self.kwargs.get('content_object_id')

        # start task or return status.
        response_dict = self.get_response_status(content_object_id=content_object_id)
        if response_dict.get('status') == 'not-created':
            self.start_compression_task(content_object_id=content_object_id)
        return JsonResponse(self.get_response_status(content_object_id=content_object_id))


class BatchCompressionAPIGroupCommentView(AbstractBatchCompressionAPIView):
    """
    API for checking if a compressed ``GroupComment`` is ready for download.
    """
    def get_ready_for_download_status(self, content_object_id=None):
        status_dict = super(BatchCompressionAPIGroupCommentView, self).get_ready_for_download_status()
        status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
            viewname='groupcomment-file-download',
            kwargs={
                'groupcomment_id': content_object_id
            })
        return status_dict

    def start_compression_task(self, content_object_id):
        group_comment = get_object_or_404(group_models.GroupComment, id=content_object_id)
        batchregistry.Registry.get_instance().run(
            actiongroup_name='batchframework_compress_groupcomment',
            context_object=group_comment
        )


class BatchCompressionAPIFeedbackSetView(AbstractBatchCompressionAPIView):
    """
    API for checking if a compressed ``FeedbackSet`` is ready for download.
    """
    def get_ready_for_download_status(self, content_object_id=None):
        status_dict = super(BatchCompressionAPIFeedbackSetView, self).get_ready_for_download_status()
        status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
            viewname='feedbackset-file-download',
            kwargs={
                'feedbackset_id': content_object_id
            })
        return status_dict

    def start_compression_task(self, content_object_id):
        feedback_set = get_object_or_404(group_models.FeedbackSet, id=content_object_id)
        batchregistry.Registry.get_instance().run(
            actiongroup_name='batchframework_compress_feedbackset',
            context_object=feedback_set)
