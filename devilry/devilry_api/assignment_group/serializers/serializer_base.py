from rest_framework import serializers


class BaseCandidateSerializer(serializers.Serializer):
    #: Full name of the candidate
    fullname = serializers.SerializerMethodField()

    #: Short name of the candidate
    shortname = serializers.SerializerMethodField()

    @property
    def devilry_role(self):
        """
        Override this to return 'student'
                                'examiner',
                                'periodadmin',
                                'subjectadmin' or
                                'departmentadmin'.

        Raises:
            :class:`NotImplementedError'
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        """
        Gets full name of the candidate or anonymized name

        Returns:
            :attr:`devilry_account.User.fullname`
        """
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.fullname

    def get_shortname(self, instance):
        """
        Gets short name of the candidate or anonymized name

        Returns:
            :attr:`devilry_account.User.shortname`
        """
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.shortname


class BaseExaminerSerializer(serializers.Serializer):
    #: Full name of the examiner.
    fullname = serializers.SerializerMethodField()

    #: Short name of the examiner.
    shortname = serializers.SerializerMethodField()

    @property
    def devilry_role(self):
        """
        Override this to return 'student'
                                'examiner',
                                'periodadmin',
                                'subjectadmin' or
                                'departmentadmin'.

        Raises:
            :class:`NotImplementedError'
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        """
        Gets full name of the examiner or anonymized name.

        Returns:
            :attr:`devilry_account.User.fullname`
        """
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.fullname

    def get_shortname(self, instance):
        """
        Gets short name of the examiner or anonymized name.

        Returns:
            :attr:`devilry_account.User.shortname`
        """
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.shortname


class AssignmentIdField(serializers.IntegerField):

    def get_attribute(self, instance):
        """
        returns the assignemnt id of the assignment group

        Args:
            instance: :obj:`devilry_group.AssignmentGroup`

        Returns:
            :attr:`devilry_group.Assignment.id`
        """
        return instance.parentnode.id


class BaseAssignmentGroupSerializer(serializers.ModelSerializer):

    #: Related assignment short name.
    assignment_short_name = serializers.SerializerMethodField()

    #: Related assignment id.
    assignment_id = AssignmentIdField()

    #: Related subject name.
    subject_short_name = serializers.SerializerMethodField()

    #: Related period name.
    period_short_name = serializers.SerializerMethodField()

    #: set to ``True`` if waiting for feedback.
    is_waiting_for_feedback = serializers.BooleanField(required=False)

    #: set to ``True`` if waiting for deliveries.
    is_waiting_for_deliveries = serializers.BooleanField(required=False)

    #: set to ``True`` if corrected
    is_corrected = serializers.BooleanField(required=False)

    # def get_assignment_id(self, instance):
    #     """
    #     Returns related assignment id.
    #
    #     Returns:
    #         :attr:`apps.core.Assignment.id`
    #     """
    #     return instance.parentnode.id

    def get_assignment_short_name(self, instance):
        """
        Returns related assignment short name.

        Returns:
            :attr:`apps.core.Assignment.short_name`
        """
        return instance.parentnode.short_name

    def get_subject_short_name(self, instance):
        """
        Returns related subject short name.

        Returns:
            :attr:`apps.core.Subject.short_name`
        """
        return instance.subject.short_name

    def get_period_short_name(self, instance):
        """
        Returns related period short name.

        Returns:
            :attr:`apps.core.Period.short_name`
        """
        return instance.period.short_name
