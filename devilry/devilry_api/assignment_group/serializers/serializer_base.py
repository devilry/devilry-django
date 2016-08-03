from rest_framework import serializers


class CandidateSerializer(serializers.Serializer):
    """
    Candidate serializer,
    subclass this and override the devilry_role property
    """

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
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        """
        Gets full name of the candidate or anonymized name
        """
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.fullname

    def get_shortname(self, instance):
        """
        Gets short name of the candidate or anonymized name
        """
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.shortname


class ExaminerSerializer(serializers.Serializer):
    """
    Examiner serializer,
    subclass this and override the devilry_role property.
    """

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
        """
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        """
        Gets full name of the examiner or anonymized name.
        """
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.fullname

    def get_shortname(self, instance):
        """
        Gets short name of the examiner or anonymized name.
        """
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.shortname


class AssignmentGroupModelSerializer(serializers.ModelSerializer):
    """
    AssignmentGroup model serializer base.
    """

    #: Related assignment long name.
    assignment_long_name = serializers.SerializerMethodField()

    #: Related assignment id.
    assignment_id = serializers.SerializerMethodField()

    #: Related subject name.
    subject_short_name = serializers.SerializerMethodField()

    #: Related period name.
    period_short_name = serializers.SerializerMethodField()

    #: set to ``True`` if waiting for feedback.
    is_waiting_for_feedback = serializers.BooleanField()

    #: set to ``True`` if waiting for deliveries.
    is_waiting_for_deliveries = serializers.BooleanField()

    #: set to ``True`` if corrected
    is_corrected = serializers.BooleanField()

    def get_assignment_id(self, instance):
        """
        Returns related assignment id.
        """
        return instance.parentnode.id

    def get_assignment_long_name(self, instance):
        """
        Returns related assignment short name.
        """
        return instance.parentnode.long_name

    def get_subject_short_name(self, instance):
        """
        Returns related subject short name.
        """
        return instance.subject.short_name

    def get_period_short_name(self, instance):
        """
        Returns related period short name.
        """
        return instance.period.short_name
