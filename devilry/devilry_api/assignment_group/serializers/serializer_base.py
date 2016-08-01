from rest_framework import serializers


class CandidateSerializer(serializers.Serializer):
    fullname = serializers.SerializerMethodField()
    shortname = serializers.SerializerMethodField()

    @property
    def devilry_role(self):
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.fullname

    def get_shortname(self, instance):
        anonymous = instance.assignment_group.parentnode. \
            students_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedstudent.user.shortname


class ExaminerSerializer(serializers.Serializer):
    fullname = serializers.SerializerMethodField()
    shortname = serializers.SerializerMethodField()

    @property
    def devilry_role(self):
        raise NotImplementedError("Please set devilry_role example: devilry_role = 'student'")

    def get_fullname(self, instance):
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.fullname

    def get_shortname(self, instance):
        anonymous = instance.assignmentgroup.parentnode. \
            examiners_must_be_anonymized_for_devilryrole(self.devilry_role)
        if anonymous:
            return instance.get_anonymous_name()
        return instance.relatedexaminer.user.shortname


class AssignmentGroupModelSerializer(serializers.ModelSerializer):
    devilryrole = None
    assignment_long_name = serializers.SerializerMethodField()
    assignment_id = serializers.SerializerMethodField()
    subject_short_name = serializers.SerializerMethodField()
    period_short_name = serializers.SerializerMethodField()
    grading_points = serializers.IntegerField()
    is_waiting_for_feedback = serializers.BooleanField()
    is_waiting_for_deliveries = serializers.BooleanField()
    is_corrected = serializers.BooleanField()

    def get_assignment_id(self, instance):
        return instance.parentnode.id

    def get_assignment_long_name(self, instance):
        return instance.parentnode.long_name

    def get_subject_short_name(self, instance):
        return instance.subject.short_name

    def get_period_short_name(self, instance):
        return instance.period.short_name
