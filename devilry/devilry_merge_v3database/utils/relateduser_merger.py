# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models


class RelatedExaminerMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.RelatedExaminer` from database to
    current default database.
    """
    model = core_models.RelatedExaminer

    def select_related_foreign_keys(self):
        return ['user', 'period', 'period__parentnode']

    def update_after_save(self, from_db_object):
        core_models.RelatedExaminer.objects\
            .filter(user__shortname=from_db_object.user.shortname,
                    period__short_name=from_db_object.period.short_name,
                    period__parentnode__short_name=from_db_object.period.parentnode.short_name)\
            .update(automatic_anonymous_id=from_db_object.automatic_anonymous_id)

    def start_migration(self, from_db_object):
        user = self.get_user_by_shortname(from_db_object.user.shortname)
        period = self.get_period_by_shortname(
            shortname=from_db_object.period.short_name,
            parentnode_shortname=from_db_object.period.parentnode.short_name)
        if user and period:
            related_examiner_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'user', 'period'])
            related_examiner = core_models.RelatedExaminer(**related_examiner_kwargs)
            related_examiner.user_id = user.id
            related_examiner.period_id = period.id
            self.save_object(obj=related_examiner)
        else:
            raise ValueError('Users, Subjects and Periods must be imported before RelatedExaminers.')


class RelatedStudentMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.RelatedStudent` from database to
    current default database.
    """
    model = core_models.RelatedStudent

    def select_related_foreign_keys(self):
        return ['user', 'period', 'period__parentnode']

    def update_after_save(self, from_db_object):
        core_models.RelatedStudent.objects\
            .filter(user__shortname=from_db_object.user.shortname,
                    period__short_name=from_db_object.period.short_name,
                    period__parentnode__short_name=from_db_object.period.parentnode.short_name)\
            .update(automatic_anonymous_id=from_db_object.automatic_anonymous_id)

    def start_migration(self, from_db_object):
        user = self.get_user_by_shortname(from_db_object.user.shortname)
        period = self.get_period_by_shortname(
            shortname=from_db_object.period.short_name,
            parentnode_shortname=from_db_object.period.parentnode.short_name)
        if user and period:
            related_student_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'user', 'period'])
            related_student = core_models.RelatedStudent(**related_student_kwargs)
            related_student.user_id = user.id
            related_student.period_id = period.id
            self.save_object(obj=related_student)
        else:
            raise ValueError('Users, Subjects and Periods must be imported before RelatedStudents.')