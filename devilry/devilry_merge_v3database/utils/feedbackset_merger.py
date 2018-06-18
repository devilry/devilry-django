# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_merge_v3database.models import TempMergeId


class FeedbackSetMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.models.FeedbackSet` from database to
    current default database.

    Note:
        Will handle merging of :class:`devilry.devilry_group.models.FeedbackSetPassedPreviousPeriod`,
        :class:`devilry.devilry_group.models.FeedbackSetGradingUpdateHistoryMerger`,
        :class:`devilry.devilry_group.models.FeedbackSetDeadlineHistoryMerger`.
    """
    model = group_models.FeedbackSet

    def select_related_foreign_keys(self):
        return [
            'group',
            'created_by',
            'last_updated_by',
            'grading_published_by',
            'group__parentnode',
            'group__parentnode__parentnode',
            'group__parentnode__parentnode__parentnode',
        ]

    def __get_created_by_user(self, feedback_set):
        if feedback_set.created_by:
            return self.get_user_by_shortname(shortname=feedback_set.created_by.shortname).id
        return None

    def __get_last_updated_by_user(self, feedback_set):
        if feedback_set.last_updated_by:
            return self.get_user_by_shortname(shortname=feedback_set.last_updated_by.shortname).id
        return None

    def __get_grading_published_by_user(self, feedback_set):
        if feedback_set.grading_published_by:
            return self.get_user_by_shortname(shortname=feedback_set.grading_published_by.shortname).id
        return None

    def __get_assignment_group_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='core_assignmentgroup',
            from_id=from_db_obj.group_id
        )
        return core_models.AssignmentGroup.objects.get(id=temp_merge_id.to_id)

    def start_migration(self, from_db_object):
        assignment_group = self.__get_assignment_group_from_temp_merge_id(from_db_obj=from_db_object)

        if assignment_group:
            feedbackset_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'group', 'created_by', 'last_updated_by', 'grading_published_by'])
            feedback_set = group_models.FeedbackSet(**feedbackset_kwargs)
            feedback_set.group_id = assignment_group.id
            feedback_set.created_by_id = self.__get_created_by_user(feedback_set=from_db_object)
            feedback_set.last_updated_by_id = self.__get_last_updated_by_user(feedback_set=from_db_object)
            feedback_set.grading_published_by_id = self.__get_grading_published_by_user(feedback_set=from_db_object)
            migrated_feedbackset = self.save_object(obj=feedback_set)

            # Create merge object from AssignmentGroup
            TempMergeId.objects.create_from_instances(
                merge_to_obj=migrated_feedbackset,
                merge_from_obj=from_db_object
            )
        else:
            raise ValueError('AssignmentGroups must be imported before FeedbackSets.')


class FeedbackSetPassedPreviousPeriodMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.FeedbackSetPassedPreviousPeriod` from database to
    current default database.
    """
    model = group_models.FeedbacksetPassedPreviousPeriod

    def select_related_foreign_keys(self):
        return [
            'feedbackset',
            'feedbackset__group',
            'feedbackset__group__parentnode',
            'feedbackset__group__parentnode__parentnode',
            'created_by',
            'grading_published_by'
        ]

    def __get_created_by_user(self, feedback_set_period_history):
        if feedback_set_period_history.created_by:
            return self.get_user_by_shortname(shortname=feedback_set_period_history.created_by.shortname).id
        return None

    def __get_grading_published_by_user(self, feedback_set_period_history):
        if feedback_set_period_history.grading_published_by:
            return self.get_user_by_shortname(shortname=feedback_set_period_history.grading_published_by.shortname).id
        return None

    def __get_feedback_set_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_group_feedbackset',
            from_id=from_db_obj.feedbackset_id
        )
        try:
            return group_models.FeedbackSet.objects.get(id=temp_merge_id.to_id)
        except group_models.FeedbackSet.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        feedback_set = self.__get_feedback_set_from_temp_merge_id(from_db_obj=from_db_object)
        if feedback_set:
            feedback_set_period_history_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'created_by', 'grading_published_by', 'feedbackset'])
            feedback_set_period_history = group_models.FeedbacksetPassedPreviousPeriod(
                **feedback_set_period_history_kwargs)
            feedback_set_period_history.feedbackset_id = feedback_set.id
            feedback_set_period_history.created_by_id = self.__get_grading_published_by_user(
                feedback_set_period_history=from_db_object)
            feedback_set_period_history.grading_published_by_id = self.__get_grading_published_by_user(
                feedback_set_period_history=from_db_object)
            self.save_object(obj=feedback_set_period_history)


class FeedbackSetGradingUpdateHistoryMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.FeedbackSetGradingUpdateHistory` from database to
    current default database.
    """
    model = group_models.FeedbackSetGradingUpdateHistory

    def select_related_foreign_keys(self):
        return [
            'feedback_set',
            'updated_by',
            'old_grading_published_by'
        ]

    def __get_updated_by_user_id(self, feedback_set_grading_history):
        if feedback_set_grading_history.updated_by:
            return self.get_user_by_shortname(
                shortname=feedback_set_grading_history.updated_by.shortname).id
        return None

    def __get_old_grading_published_by_user_id(self, feedback_set_grading_history):
        if feedback_set_grading_history.old_grading_published_by:
            return self.get_user_by_shortname(
                shortname=feedback_set_grading_history.old_grading_published_by.shortname).id
        return None

    def __get_feedback_set_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_group_feedbackset',
            from_id=from_db_obj.feedback_set_id
        )
        try:
            return group_models.FeedbackSet.objects.get(id=temp_merge_id.to_id)
        except group_models.FeedbackSet.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        feedback_set = self.__get_feedback_set_from_temp_merge_id(from_db_obj=from_db_object)

        if feedback_set:
            feedback_set_grading_history_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'feedback_set', 'updated_by', 'old_grading_published_by'])
            feedback_set_grading_history = group_models.FeedbackSetGradingUpdateHistory(
                **feedback_set_grading_history_kwargs)
            feedback_set_grading_history.feedback_set_id = feedback_set.id
            feedback_set_grading_history.updated_by_id = self.__get_updated_by_user_id(
                feedback_set_grading_history=from_db_object)
            feedback_set_grading_history.old_grading_published_by_id = self.__get_old_grading_published_by_user_id(
                feedback_set_grading_history=from_db_object)
            self.save_object(obj=feedback_set_grading_history)


class FeedbackSetDeadlineHistoryMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.models.FeedbackSetGradingUpdateHistory` from database to
    current default database.
    """
    model = group_models.FeedbackSetDeadlineHistory

    def select_related_foreign_keys(self):
        return [
            'feedback_set',
            'changed_by'
        ]

    def __get_changed_by_user(self, feedback_set_deadline_history):
        if feedback_set_deadline_history.changed_by:
            return self.get_user_by_shortname(shortname=feedback_set_deadline_history.changed_by.shortname)

    def __get_feedback_set_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_group_feedbackset',
            from_id=from_db_obj.feedback_set_id
        )
        try:
            return group_models.FeedbackSet.objects.get(id=temp_merge_id.to_id)
        except group_models.FeedbackSet.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        feedback_set = self.__get_feedback_set_from_temp_merge_id(from_db_obj=from_db_object)

        if feedback_set:
            feedback_set_deadline_history_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'feedback_set', 'changed_by'
            ])
            feedback_set_deadline_history = group_models.FeedbackSetDeadlineHistory(**feedback_set_deadline_history_kwargs)
            feedback_set_deadline_history.feedback_set_id = feedback_set.id
            feedback_set_deadline_history.changed_by_id = self.__get_changed_by_user(
                feedback_set_deadline_history=feedback_set_deadline_history)
            self.save_object(obj=feedback_set_deadline_history)