from rest_framework import serializers

from devilry.apps.core.models import Examiner


class FeedbacksetModelSerializer(serializers.ModelSerializer):
    """
    Feedbackset model serializer for :class:`~devilry_group.FeedbackSet`
    """
    created_by_fullname = serializers.SerializerMethodField()
    deadline_datetime = serializers.SerializerMethodField()

    @property
    def devilry_role(self):
        """
        Override this to return 'student'
                                'examiner',
                                'periodadmin',
                                'subjectadmin' or
                                'departmentadmin'.
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_created_by_fullname(self, instance):
        """
        Gets full name of the examiner or anonymized name.

        TODO: admin stuffs

        Args:
            instance: :obj:`~devilry_group.Feedbackset`

        Returns:
            full name of anonymized name (str)
        """
        anonymous = instance.group.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        try:
            examiner = Examiner.objects.get(assignmentgroup=instance.group,
                                            relatedexaminer__user=instance.created_by)

        except Examiner.DoesNotExist:
            return 'Admin'
        if anonymous:
            return examiner.get_anonymous_name()
        return instance.created_by.fullname

    def get_deadline_datetime(self, instance):
        """
        Returns the current deadline

        Args:
            instance: :obj:`~devilry_group.Feedbackset`

        Returns:
            current deadline (DateTime)

        """
        return instance.current_deadline()