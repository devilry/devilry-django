from django.utils.translation import ugettext_lazy
from ievv_opensource.ievv_batchframework import batchregistry
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from devilry.devilry_api.auth.authentication import TokenAuthentication
from devilry.devilry_compressionutil import models as archive_models
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group.utils.download_response import download_response


class BaseFeedbacksetView(APIView):

    authentication_classes = (TokenAuthentication,)

    @property
    def permission_classes(self):
        """
        Permission classes required

        Example:
            permission_classes = (IsAuthenticated, )

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    @property
    def api_key_permissions(self):
        """
        Should be a list with API key permissions :class:`devilry_api.APIKey`.

        Example:
            api_key_permissions = (:attr:`APIKey.STUDENT_PERMISSION_WRITE`, :attr:`APIKey.STUDENT_PERMISSION_READ`)

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError(
            "please set api_key_permission example: "
            "api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)")

    def get_role_queryset(self):
        """
        Returns queryset for role (examiner, student etc...).

        Should return a queryset of :class:`~devilry_group.Feedbackset`

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError(ugettext_lazy('Please implement get role queryset'))

    def get(self, request, content_id, *args, **kwargs):
        """
        Download files for feedbackset zipped

        ---
        parameters:
            - name: content_id
              paramType: path
              required: True
              description: id of feedbackset to download

        """
        # Check that request user has access to feedbackset and if it exists.
        try:
            feedbackset = self.get_role_queryset().get(id=content_id)
        except FeedbackSet.DoesNotExist:
            raise NotFound(ugettext_lazy('Feedbackset not found'))
        # Check if feedbackset is already compressed.
        archive_meta = archive_models.CompressedArchiveMeta.objects.filter(content_object_id=content_id).first()
        if archive_meta:
            return download_response(content_path=archive_meta.archive_path,
                                     content_size=archive_meta.archive_size,
                                     content_type='application/zip',
                                     content_name=archive_meta.archive_name)
        # Compress Feedbackset
        batchregistry.Registry.get_instance().run(
            actiongroup_name='batchframework_api_compress_feedbackset',
            context_object=feedbackset,
            test='test'
        )

        # Get archive
        try:
            archive_meta = archive_models.CompressedArchiveMeta.objects.get(content_object_id=content_id)
        except archive_models.CompressedArchiveMeta.DoesNotExist:
            raise NotFound(ugettext_lazy('Compressed Archive not found'))

        # Return download response
        return download_response(content_path=archive_meta.archive_path,
                                 content_size=archive_meta.archive_size,
                                 content_type='application/zip',
                                 content_name=archive_meta.archive_name)
