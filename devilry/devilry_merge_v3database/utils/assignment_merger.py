# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.apps.core import models as core_models


class AssignmentMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.Assignment` from database to
    current default database.
    """
    model = core_models.Assignment

    def select_related_foreign_keys(self):
        return ['parentnode', 'parentnode__parentnode']

    def start_migration(self, from_db_object):
        period = self.get_period_by_shortname(parentnode_shortname=from_db_object.parentnode.parentnode.short_name,
                                              shortname=from_db_object.parentnode.short_name)
        if period:
            assignment_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'parentnode', 'admins'])
            assignment = core_models.Assignment(**assignment_kwargs)
            assignment.parentnode_id = period.id
            self.save_object(obj=assignment)
        else:
            raise ValueError('Periods must be imported before Assignments.')
