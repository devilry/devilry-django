# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models


class AssignmentGroupMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.AssignmentGroup` from database to
    current default database.
    """
    model = core_models.AssignmentGroup

    def select_related_foreign_keys(self):
        return [
            'parentnode',
            'parentnode__parentnode',
            'parentnode__parentnode__parentnode'
        ]

    def update_after_save(self, from_db_object):
        core_models.AssignmentGroup.objects.filter(
            parentnode__parentnode__parentnode__short_name=from_db_object.parentnode.parentnode.parentnode.short_name,
            parentnode__parentnode__short_name=from_db_object.parentnode.parentnode.short_name,
            parentnode__short_name=from_db_object.parentnode.short_name
        ).update(etag=from_db_object.etag)

    def start_migration(self, from_db_object):
        assignment = self.get_assignment_by_shortname(
            parentnode_parentnode_shortname=from_db_object.parentnode.parentnode.parentnode.short_name,
            parentnode_shortname=from_db_object.parentnode.parentnode.short_name,
            shortname=from_db_object.parentnode.short_name
        )
        if assignment:
            assignmentgroup_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'parentnode', 'batchoperation', 'copied_from', 'feedback', 'last_deadline'])
            assignment_group = core_models.AssignmentGroup(**assignmentgroup_kwargs)
            assignment_group.parentnode_id = assignment.id
            migrated_assignment_group = self.save_object(obj=assignment_group)

            # Migrate candidates
            CandidateMerger(
                migrated_assignment_group=migrated_assignment_group,
                from_db_alias=self.from_db_alias,
                queryset_manager=from_db_object.candidates).run()

            # Migrate examiners
            ExaminerMerger(
                migrated_assignment_group=migrated_assignment_group,
                from_db_alias=self.from_db_alias,
                queryset_manager=from_db_object.examiners).run()

            FeedbackSetMerger(
                migrated_assignment_group=migrated_assignment_group,
                from_db_alias=self.from_db_alias,
                queryset_manager=from_db_object.feedbackset_set).run()

        else:
            raise ValueError('Assignments must be imported before AssignmentGroups.')


class AbstractAssignmentGroupRelatedModelMerger(merger.AbstractMerger):
    """
    Abstract class merger for models that has AssignmentGroup as a direct relation.
    """
    def __init__(self, migrated_assignment_group, *args, **kwargs):
        self.migrated_assignment_group = migrated_assignment_group
        super(AbstractAssignmentGroupRelatedModelMerger, self).__init__(*args, **kwargs)


class CandidateMerger(AbstractAssignmentGroupRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.Candidate` from database to
    current default database.
    """
    model = core_models.Candidate

    def select_related_foreign_keys(self):
        return [
            'assignment_group',
            'relatedstudent',
            'relatedstudent__user',
            'relatedstudent__period',
            'relatedstudent__period__parentnode'
        ]

    def start_migration(self, from_db_object):
        relatedstudent = self.get_relatedstudent(
            user_shortname=from_db_object.relatedstudent.user.shortname,
            period_shortname=from_db_object.relatedstudent.period.short_name,
            subject_shortname=from_db_object.relatedstudent.period.parentnode.short_name)
        if relatedstudent:
            candidate_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'assignment_group', 'relatedstudent', 'old_reference_not_in_use_student'])
            candidate = core_models.Candidate(**candidate_kwargs)
            candidate.assignment_group_id = self.migrated_assignment_group.id
            candidate.relatedstudent_id = relatedstudent.id
            self.save_object(obj=candidate)
        else:
            raise ValueError('RelatedStudents must be imported before Candidates')


class ExaminerMerger(AbstractAssignmentGroupRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.Examiner` from database to
    current default database.
    """
    model = core_models.Examiner

    def select_related_foreign_keys(self):
        return [
            'assignmentgroup',
            'relatedexaminer',
            'relatedexaminer__user',
            'relatedexaminer__period',
            'relatedexaminer__period__parentnode'
        ]

    def start_migration(self, from_db_object):
        relatedexaminer = self.get_relatedexaminer(
            user_shortname=from_db_object.relatedexaminer.user.shortname,
            period_shortname=from_db_object.relatedexaminer.period.short_name,
            subject_shortname=from_db_object.relatedexaminer.period.parentnode.short_name)
        if relatedexaminer:
            examiner_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'assignmentgroup', 'relatedexaminer', 'old_reference_not_in_use_user'])
            examiner = core_models.Examiner(**examiner_kwargs)
            examiner.assignmentgroup_id = self.migrated_assignment_group.id
            examiner.relatedexaminer_id = relatedexaminer.id
            self.save_object(obj=examiner)
        else:
            raise ValueError('RelatedExaminers must be imported before Candidates')


class FeedbackSetMerger(AbstractAssignmentGroupRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.FeedbackSet` from database to
    current default database.
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

    def start_migration(self, from_db_object):
        feedbackset_kwargs = model_to_dict(from_db_object, exclude=[
            'id', 'pk', 'group', 'created_by', 'last_updated_by', 'grading_published_by'])
        feedback_set = group_models.FeedbackSet(**feedbackset_kwargs)
        feedback_set.group_id = self.migrated_assignment_group.id
        feedback_set.created_by_id = self.__get_created_by_user(feedback_set=from_db_object)
        feedback_set.last_updated_by_id = self.__get_last_updated_by_user(feedback_set=from_db_object)
        feedback_set.grading_published_by_id = self.__get_grading_published_by_user(feedback_set=from_db_object)
        migrated_feedback_set = self.save_object(obj=feedback_set)

        # Merge FeedbackSetPassedPreviousPeriod
        if group_models.FeedbacksetPassedPreviousPeriod.objects.using(self.from_db_alias)\
                .filter(feedbackset_id=from_db_object.id)\
                .exists():
            FeedbackSetPassedPreviousPeriodMerger(
                migrated_feedback_set=migrated_feedback_set,
                from_db_alias=self.from_db_alias,
                queryset_manager=from_db_object.feedbackset_passed_previous_period)

        # Merge FeedbackSetGradingUpdateHistory
        FeedbackSetGradingUpdateHistoryMerger(
            migrated_feedback_set=migrated_feedback_set,
            from_db_alias=self.from_db_alias,
            queryset_manager=from_db_object.grading_update_histories).run()

        # Merge FeedbackSetDeadlineHistory
        FeedbackSetDeadlineHistoryMerger(
            migrated_feedback_set=migrated_feedback_set,
            from_db_alias=self.from_db_alias,
            queryset_manager=from_db_object.feedbacksetdeadlinehistory_set).run()


class AbstractFeedbackSetRelatedModelMerger(merger.AbstractMerger):
    """
    Abstract class merger for models that has AssignmentGroup as a direct relation.
    """

    def __init__(self, migrated_feedback_set, *args, **kwargs):
        self.migrated_feedback_set = migrated_feedback_set
        super(AbstractFeedbackSetRelatedModelMerger, self).__init__(*args, **kwargs)


class FeedbackSetPassedPreviousPeriodMerger(AbstractFeedbackSetRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.FeedbackSetPassedPreviousPeriod` from database to
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

    def start_migration(self, from_db_object):
        feedback_set_period_history_kwargs = model_to_dict(from_db_object, exclude=[
            'id', 'pk', 'created_by', 'grading_published_by', 'feedbackset'])
        feedback_set_period_history = group_models.FeedbacksetPassedPreviousPeriod(
            **feedback_set_period_history_kwargs)
        feedback_set_period_history.created_by_id = self.__get_grading_published_by_user(
            feedback_set_period_history=from_db_object)
        feedback_set_period_history.grading_published_by_id = self.__get_grading_published_by_user(
            feedback_set_period_history=from_db_object)
        self.save_object(obj=feedback_set_period_history)


class FeedbackSetGradingUpdateHistoryMerger(AbstractFeedbackSetRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.FeedbackSetGradingUpdateHistory` from database to
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

    def start_migration(self, from_db_object):
        feedback_set_grading_history_kwargs = model_to_dict(from_db_object, exclude=[
            'id', 'pk', 'feedback_set', 'updated_by', 'old_grading_published_by'])
        feedback_set_grading_history = group_models.FeedbackSetGradingUpdateHistory(
            **feedback_set_grading_history_kwargs)
        feedback_set_grading_history.feedback_set_id = self.migrated_feedback_set.id
        feedback_set_grading_history.updated_by_id = self.__get_updated_by_user_id(
            feedback_set_grading_history=from_db_object)
        feedback_set_grading_history.old_grading_published_by_id = self.__get_old_grading_published_by_user_id(
            feedback_set_grading_history=from_db_object)
        self.save_object(obj=feedback_set_grading_history)


class FeedbackSetDeadlineHistoryMerger(AbstractFeedbackSetRelatedModelMerger):
    """
    Merge :class:`devilry.apps.core.models.FeedbackSetGradingUpdateHistory` from database to
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

    def start_migration(self, from_db_object):
        feedback_set_deadline_history_kwargs = model_to_dict(from_db_object, exclude=[
            'id', 'pk', 'feedback_set', 'changed_by'
        ])
        feedback_set_deadline_history = group_models.FeedbackSetDeadlineHistory(**feedback_set_deadline_history_kwargs)
        feedback_set_deadline_history.feedback_set_id = self.migrated_feedback_set.id
        feedback_set_deadline_history.changed_by_id = self.__get_changed_by_user(
            feedback_set_deadline_history=feedback_set_deadline_history)
        self.save_object(obj=feedback_set_deadline_history)
