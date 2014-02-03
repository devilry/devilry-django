from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError

from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
# from devilry.apps.core.models import Assignment
from devilry.apps.core.models import GroupInvite


class TestGroupInvite(TestCase):
    def setUp(self):
        self.testuser1 = UserBuilder('testuser1').user
        self.testuser2 = UserBuilder('testuser2').user

    def test_create_sanity(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=True)\
            .add_group().group
        before = datetime.now()
        invite = group.groupinvite_set.create(
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        after = datetime.now()
        self.assertTrue(invite.sent_datetime >= before and invite.sent_datetime <= after)