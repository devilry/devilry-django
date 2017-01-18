# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http.response import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import View
from ievv_opensource.ievv_batchframework import batchregistry

from devilry.devilry_compressionutil import models as compression_models


class BatchCompressionAPIView(View):
    """

    """
    def _verify_json(self, posted_data):
        """

        Args:
            posted_data ():

        Returns:
            dict: json as dictionary or None.
        """
        try:
            json_dict = json.loads(posted_data)
        except ValueError:
            return None
        return json_dict

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        # post / start zipping.
        return self.json_response()

    def json_response(self, json_data):
        return JsonResponse(json_data)


class BatchCompressionAPIGroupCommentView(BatchCompressionAPIView):
    """

    """
    def get(self, request, *args, **kwargs):
        super(BatchCompressionAPIGroupCommentView, self).get(request, *args, **kwargs)
        groupcomment_id = kwargs.get('groupcomment_id')
        try:
            archived_meta = compression_models.CompressedArchiveMeta.objects.get(content_object_id=groupcomment_id)
        except compression_models.CompressedArchiveMeta.DoesNotExist:
            batchoperation = batchregistry.Registry\
                .get_actiongroup(actiongroup_name='batchframework_compress_groupcomment')



    def post(self, request, *args, **kwargs):
        super(BatchCompressionAPIGroupCommentView, self).post(request, *args, **kwargs)


class BatchCompressionAPIFeedbackSetView(BatchCompressionAPIView):
    """

    """
    def get(self, request, *args, **kwargs):
        return super(BatchCompressionAPIFeedbackSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BatchCompressionAPIFeedbackSetView, self).post(request, *args, **kwargs)

# not started
# running
# finished
# finished, return with url