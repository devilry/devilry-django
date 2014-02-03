from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# from django.core.exceptions import ValidationError

from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
# from devilry.apps.core.models import Assignment
from devilry.apps.core.models import GroupInvite


class TestGroupInvite(TestCase):
    def setUp(self):
        self.testuser1 = UserBuilder('testuser1').user
        self.testuser2 = UserBuilder('testuser2').user
        self.testuser3 = UserBuilder('testuser3').user

    def test_create_sanity(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        before = datetime.now()
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        invite.full_clean()
        invite.save()
        after = datetime.now()
        self.assertTrue(invite.sent_datetime >= before and invite.sent_datetime <= after)

    def test_only_groupmember_can_invite(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        with self.assertRaises(ValidationError):
            GroupInvite(group=group, sent_by=self.testuser2, sent_to=self.testuser3).clean()

    def test_can_not_invite_groupmember(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1, self.testuser2]).group
        with self.assertRaises(ValidationError):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser2).clean()

    def test_can_not_invite_self(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        with self.assertRaises(ValidationError):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser1).clean()

    def test_only_when_allowed_on_assignment(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_create_groups=False)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        with self.assertRaises(ValidationError):
            invite.full_clean()

    def test_students_can_not_create_groups_after(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                passing_grade_min_points=1,
                students_can_not_create_groups_after=DateTimeBuilder.now().minus(days=1),
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        with self.assertRaises(ValidationError):
            invite.full_clean()