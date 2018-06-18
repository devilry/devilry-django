# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_merge_v3database.models import TempMergeId


class AssignmentGroupMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.AssignmentGroup` from database to
    current default database.

    Note:
        Will handle merging of :class:`devilry.apps.core.models.Candidate`s,
        :class:`devilry.apps.core.models.Examiners`s and :class:`devilry.devilry_group.models.FeedbackSet`s as we
        have no way of identifying an imported `AssignmentGroup` from the database it was imported from.
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

            # Create merge object from AssignmentGroup
            TempMergeId.objects.create_from_instances(
                merge_to_obj=migrated_assignment_group,
                merge_from_obj=from_db_object
            )
        else:
            raise ValueError('Assignments must be imported before AssignmentGroups.')


class AbstractAssignmentGroupRelatedModelMerger(merger.AbstractMerger):
    """
    Abstract class merger for models that has AssignmentGroup as a direct relation.
    """
    def __init__(self, migrated_assignment_group, *args, **kwargs):
        self.migrated_assignment_group = migrated_assignment_group
        super(AbstractAssignmentGroupRelatedModelMerger, self).__init__(*args, **kwargs)


class CandidateMerger(merger.AbstractMerger):
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

    def __get_assignment_group_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='core_assignmentgroup',
            from_id=from_db_obj.assignment_group_id
        )
        return core_models.AssignmentGroup.objects.get(id=temp_merge_id.to_id)

    def start_migration(self, from_db_object):
        relatedstudent = self.get_relatedstudent(
            user_shortname=from_db_object.relatedstudent.user.shortname,
            period_shortname=from_db_object.relatedstudent.period.short_name,
            subject_shortname=from_db_object.relatedstudent.period.parentnode.short_name)
        assignment_group = self.__get_assignment_group_from_temp_merge_id(from_db_obj=from_db_object)
        if relatedstudent and assignment_group:
            candidate_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'assignment_group', 'relatedstudent', 'old_reference_not_in_use_student'])
            candidate = core_models.Candidate(**candidate_kwargs)
            candidate.assignment_group_id = assignment_group.id
            candidate.relatedstudent_id = relatedstudent.id
            self.save_object(obj=candidate)
        else:
            raise ValueError('RelatedStudents and AssignmentGroups must be imported before Candidates')


class ExaminerMerger(merger.AbstractMerger):
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

    def __get_assignment_group_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='core_assignmentgroup',
            from_id=from_db_obj.assignmentgroup_id
        )
        return core_models.AssignmentGroup.objects.get(id=temp_merge_id.to_id)

    def start_migration(self, from_db_object):
        relatedexaminer = self.get_relatedexaminer(
            user_shortname=from_db_object.relatedexaminer.user.shortname,
            period_shortname=from_db_object.relatedexaminer.period.short_name,
            subject_shortname=from_db_object.relatedexaminer.period.parentnode.short_name)
        assignment_group = self.__get_assignment_group_from_temp_merge_id(from_db_obj=from_db_object)
        if relatedexaminer and assignment_group:
            examiner_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'assignmentgroup', 'relatedexaminer', 'old_reference_not_in_use_user'])
            examiner = core_models.Examiner(**examiner_kwargs)
            examiner.assignmentgroup_id = assignment_group.id
            examiner.relatedexaminer_id = relatedexaminer.id
            self.save_object(obj=examiner)
        else:
            raise ValueError('RelatedExaminers and AssignmentGroups must be imported before Candidates')
