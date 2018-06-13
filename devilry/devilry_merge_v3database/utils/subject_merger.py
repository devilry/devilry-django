# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models


class SubjectMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.apps.core.models.Subject` from database to
    current default database.
    """
    model = core_models.Subject

    def start_migration(self, from_db_object):
        subject_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'admins'])
        subject = core_models.Subject(**subject_kwargs)
        self.save_object(obj=subject)
