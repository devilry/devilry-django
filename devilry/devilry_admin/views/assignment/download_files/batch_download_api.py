# -*- coding: utf-8 -*-


from ievv_opensource.ievv_batchframework import batchregistry
from django.http.response import JsonResponse

from devilry.apps.core import models as core_models
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_group.models import GroupComment, FeedbackSet
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.views.download_files.batch_download_api import AbstractBatchCompressionAPIView


class BatchCompressionAPIAssignmentView(AbstractBatchCompressionAPIView):
    """
    API for checking if a compressed ``Assignment`` is ready for download.
    """
    model_class = core_models.Assignment
    batchoperation_type = 'batchframework_admin_compress_assignment'

    @property
    def created_by_role(self):
        return CompressedArchiveMeta.CREATED_BY_ROLE_ADMIN

    def get_assignment_group_ids(self):
        assignment_group_ids = core_models.AssignmentGroup.objects \
            .filter(parentnode=self.content_object) \
            .filter_user_is_admin(user=self.request.user) \
            .values_list('id', flat=True)
        return assignment_group_ids

    def __get_comment_file_queryset(self):
        group_comment_ids = GroupComment.objects \
            .filter(feedback_set__group_id__in=self.get_assignment_group_ids()) \
            .values_list('id', flat=True)
        return CommentFile.objects \
            .filter(comment_id__in=group_comment_ids)

    def has_no_files(self):
        return not FeedbackSet.objects\
            .filter_public_comment_files_from_students()\
            .filter(group__parentnode=self.content_object)\
            .exists()

    def new_files_added(self, latest_compressed_datetime):
        return self.__get_comment_file_queryset()\
            .filter(created_datetime__gt=latest_compressed_datetime)\
            .exists()

    def get_ready_for_download_status(self, content_object_id=None):
        status_dict = super(BatchCompressionAPIAssignmentView, self).get_ready_for_download_status()
        status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
            viewname='assignment-file-download',
            kwargs={
                'assignment_id': content_object_id
            })
        return status_dict

    def should_filter_by_created_by_user(self):
        return True

    def get(self, request, *args, **kwargs):
        content_object_id = kwargs.get('content_object_id')
        return JsonResponse(self.get_ready_for_download_status(content_object_id=content_object_id))

    def start_compression_task(self, content_object_id):
        batchregistry.Registry.get_instance().run(
            actiongroup_name=self.batchoperation_type,
            context_object=self.content_object,
            operationtype=self.batchoperation_type,
            started_by=self.request.user
        )
