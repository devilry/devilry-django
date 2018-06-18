import datetime

import pytz
from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_merge_v3database.utils import assignment_merger


class TestAssignmentGroupMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True


