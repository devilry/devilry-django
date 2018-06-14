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

    def start_migration(self, from_db_object):
        user = self.get_user_by_shortname(from_db_object.user.shortname)
        period = self.get_period_by_shortname(
            shortname=from_db_object.period.short_name,
            parentnode_shortname=from_db_object.period.parentnode.short_name)
        if user and period:
            pass
        else:
            raise ValueError('Users and Periods must be imported before RelatedExaminers.')


class RelatedStudentMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.RelatedStudent` from database to
    current default database.
    """
    model = core_models.RelatedStudent

    def select_related_foreign_keys(self):
        return ['user', 'period', 'period__parentnode']

    def start_migration(self, from_db_object):
        user = self.get_user_by_shortname(from_db_object.user.shortname)
        period = self.get_period_by_shortname(
            shortname=from_db_object.period.short_name,
            parentnode_shortname=from_db_object.period.parentnode.short_name)
        if user and period:
            pass
        else:
            raise ValueError('Users and Periods must be imported before RelatedStudents.')