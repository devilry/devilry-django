from django.utils.timezone import datetime
from rest_framework import serializers

from django.utils.translation import ugettext_lazy
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.feedbackset.serializers import serializer_base
from devilry.devilry_group.models import FeedbackSet


class FeedbacksetSerializerExaminer(serializer_base.FeedbacksetSerializerBase):
    FEEDBACKSET_CHOICES = [
        (FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT, 'new attempt'),
        (FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT, 're edit')
    ]

    devilry_role = 'examiner'

    def validate_group_id(self, value):
        """
        Make sure that examiner is part of assignment group

        Args:
            value: :obj:`~core.AssignemntGroup.id`

        Returns:
            :obj:`~core.AssignemntGroup.id`
        """
        try:
            AssignmentGroup.objects \
                .filter_examiner_has_access(user=self.context['request'].user) \
                .get(id=value)
        except AssignmentGroup.DoesNotExist:
            raise serializers.ValidationError(ugettext_lazy('Access denied ' 'Examiner not part of assignment group'))
        return value

    def validate_deadline_datetime(self, value):
        """
        Make sure that deadline is not in the past

        TODO: we could also check if the previous set deadline has expired
        Returns:
            datetime (DateTime)

        """
        if value < datetime.now():
            raise serializers.ValidationError(ugettext_lazy('Deadline must be in the future'))
        return value

    def validate_feedbackset_type(self, value):
        """
        TODO: validate that the previous set is first_attempt or new_attempt if
        value is new_attempt etc..
        Args:
            value: :obj:`~devilry_group.Feedbackset.feedbackset_type`

        Returns:
            :obj:`~devilry_group.Feedbackset.feedbackset_type`
        """
        if value not in [FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT, FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT]:
            raise serializers.ValidationError(
                ugettext_lazy('Examiner can only create feedbacksets with feedbackset_type: {} and {}'.format(
                              FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT, FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT)))
        return value

    def validate(self, data):
        """
        Checks existence of required data and makes sure that any other data than group, and feedbackset_type is ignored,
        rest of the data will be set automatically.

        Returns:
            dict with group, deadline_datetime and feedbackset_type
        """
        # checks existence
        if 'group_id' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'group_id missing.'))
        if 'feedbackset_type' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'feedbackset_type missing.'))
        if 'deadline_datetime' not in data:
            raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'deadline_datetime missing.'))

        # ignore any other data
        validated_data = dict()
        validated_data['group_id'] = data['group_id']
        validated_data['feedbackset_type'] = data['feedbackset_type']
        validated_data['deadline_datetime'] = data['deadline_datetime']
        return validated_data

    def __set_is_last_in_group_false_in_previous_feedbackset(self, group_id):
        """
        Sets the attribute :obj:`~devilry_group.Feedbackset.is_last_in_group` for the previous
         feedbackset to False
        Args:
            group: :obj:`~core.AssignmentGroup.id`
        """
        previous_feedback_set = FeedbackSet.objects.filter(group__id=group_id, is_last_in_group=True).first()
        if not previous_feedback_set:
            return
        previous_feedback_set.is_last_in_group = False
        previous_feedback_set.save()

    def create(self, validated_data):
        """
        Creates a new feedbackset

        Args:
            validated_data: dictionary

        Returns:
            :obj:`~devilry_group.Feedbackset`

        """
        self.__set_is_last_in_group_false_in_previous_feedbackset(validated_data['group_id'])
        return FeedbackSet.objects.create(created_by=self.context['request'].user, **validated_data)


# class FeedbacksetModelSerializer(serializer_base.FeedbacksetModelSerializer):
#
#     devilry_role = 'examiner'
#
#     class Meta:
#         model = FeedbackSet
#         fields = [
#             'id',
#             'group',
#             'created_datetime',
#             'feedbackset_type',
#             'is_last_in_group',
#             'deadline_datetime',
#             'created_by_fullname',
#         ]
#
#     def validate_patch(self, data):
#         """
#         checks that selected feedback deadline_datetime has expired
#
#         Returns:
#             Empty dictionary
#
#         """
#         if not self.instance.current_deadline() or self.instance.current_deadline() < datetime.now():
#             raise serializers.ValidationError(ugettext_lazy('deadline has not expired yet'))
#         return {}
#
#     def validate_post(self, data):
#         """
#         Checks existence of required data and makes sure that any other data than group, and feedbackset_type is ignored,
#         rest of the data will be set automatically.
#
#         Returns:
#             dict with group, deadline_datetime and feedbackset_type
#         """
#         # checks existence
#         if 'group' not in data:
#             raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'group missing.'))
#         if 'feedbackset_type' not in data:
#             raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'feedbackset_type missing.'))
#         if 'deadline_datetime' not in data:
#             raise serializers.ValidationError(ugettext_lazy('Data missing: ' 'deadline_datetime missing.'))
#
#         # ignore any other data
#         validated_data = dict()
#         validated_data['group'] = data['group']
#         validated_data['feedbackset_type'] = data['feedbackset_type']
#         validated_data['deadline_datetime'] = data['deadline_datetime']
#         return validated_data
#
#     def validate(self, data):
#         """
#         validate router
#         Returns: validated data
#
#         """
#
#         if self.partial:
#             return self.validate_patch(data)
#         return self.validate_post(data)
#
#     def validate_is_last_in_group(self, value):
#         """
#         Because of is_last_in_group and group is unique together,
#         this is needed to pass validation.
#         Later on before the model is created we will set the old
#         feedbackset's is_last_in_group to false and the new to true
#
#         Returns:
#             ``False``
#         """
#         return False
#
#     def validate_group(self, value):
#         """
#         Make sure that examiner is part of assignment group
#
#         Args:
#             value: :obj:`~core.AssignemntGroup`
#
#         Returns:
#             :obj:`~core.AssignemntGroup`
#         """
#         try:
#             AssignmentGroup.objects \
#                 .filter_examiner_has_access(user=self.context['request'].user) \
#                 .get(id=value.id)
#         except AssignmentGroup.DoesNotExist:
#             raise serializers.ValidationError(ugettext_lazy('Access denied' 'Examiner not part of assignment group'))
#         return value
#
#     def validate_deadline_datetime(self, value):
#         """
#         Make sure that deadline is not in the past
#
#         TODO: we could also check if the previous set deadline has expired
#         Returns:
#             datetime (DateTime)
#
#         """
#         if value < datetime.now():
#             raise serializers.ValidationError(ugettext_lazy('Deadline must be in the future'))
#         return value
#
#     def validate_feedbackset_type(self, value):
#         """
#         TODO: validate that the previous set is first_attempt or new_attempt if
#         value is new_attempt etc..
#         Args:
#             value: :obj:`~devilry_group.Feedbackset.feedbackset_type`
#
#         Returns:
#             :obj:`~devilry_group.Feedbackset.feedbackset_type`
#         """
#         if value not in [FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT, FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT]:
#             raise serializers.ValidationError(
#                 ugettext_lazy('Examiner can only create feedbacksets with feedbackset_type: {} and {}'.format(
#                               FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT, FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT)))
#         return value
#
#     def __set_is_last_in_group_false_in_previous_feedbackset(self, group):
#         """
#         Sets the attribute :obj:`~devilry_group.Feedbackset.is_last_in_group` for the previous
#          feedbackset to False
#         Args:
#             group: :obj:`~core.AssignmentGroup`
#         """
#         previous_feedback_set = FeedbackSet.objects.filter(group=group, is_last_in_group=True).first()
#         if not previous_feedback_set:
#             return
#         previous_feedback_set.is_last_in_group = False
#         previous_feedback_set.save()
#
#     def create(self, validated_data):
#         """
#         Creates a new feedbackset
#
#         Args:
#             validated_data: dictionary
#
#         Returns:
#             :obj:`~devilry_group.Feedbackset`
#
#         """
#         self.__set_is_last_in_group_false_in_previous_feedbackset(validated_data['group'])
#         return FeedbackSet.objects.create(created_by=self.context['request'].user, **validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         TODO: publish feedback
#         Args:
#             instance: :obj:`~devilry_group.Feedbackset`
#             validated_data: dictionary
#
#         Returns:
#
#         """
#         pass