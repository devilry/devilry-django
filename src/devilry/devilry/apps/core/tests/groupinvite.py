from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry.apps.core.models import GroupInvite


class TestGroupInvite(TestCase):
    def setUp(self):
        self.testuser1 = UserBuilder('testuser1').user
        self.testuser2 = UserBuilder('testuser2').user
        self.testuser3 = UserBuilder('testuser3').user

    def test_create_sanity(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
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
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The user sending an invite must be a Candiate on the group.*$'):
            GroupInvite(group=group, sent_by=self.testuser2, sent_to=self.testuser3).clean()

    def test_can_not_invite_groupmember(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1, self.testuser2]).group
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The student is already a member of the group.*$'):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser2).clean()

    def test_can_not_invite_self(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The student is already a member of the group.*$'):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser1).clean()

    def test_only_when_allowed_on_assignment(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_create_groups=False)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        with self.assertRaisesRegexp(ValidationError,
                r'^.*This assignment does not allow students to form project groups on their own.*$'):
            invite.full_clean()

    def test_students_can_not_create_groups_after(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_not_create_groups_after=DateTimeBuilder.now().minus(days=1),
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        with self.assertRaisesRegexp(ValidationError,
                r'^.*Creating project groups without administrator approval is not allowed on this assignment anymore.*$'):
            invite.full_clean()

    def test_invited_student_must_be_relatedstudent(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The invited student is not registered on this subject.*$'):
            invite.full_clean()

    def test_respond(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        invite.save()
        self.assertIsNone(invite.accepted)

        before = datetime.now()
        invite.respond(accepted=True)
        after = datetime.now()
        self.assertTrue(invite.accepted)
        self.assertTrue(invite.responded_datetime >= before and invite.responded_datetime <= after)

    def test_accepted_email(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        
        self.assertEqual(len(mail.outbox), 0)
        invite.respond(accepted=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['testuser1@example.com'])
        self.assertEqual(mail.outbox[0].subject, '[Devilry] testuser2 accepted your project group invite')
        self.assertIn(
            u'testuser2 accepted the invite to join your project\ngroup for duck1010 assignment1',
            mail.outbox[0].body)

    def test_rejected_email(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        
        self.assertEqual(len(mail.outbox), 0)
        invite.respond(accepted=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['testuser1@example.com'])
        self.assertEqual(mail.outbox[0].subject, '[Devilry] testuser2 rejected your project group invite')
        self.assertIn(
            u'testuser2 rejected the invite to join your project\ngroup for duck1010 assignment1',
            mail.outbox[0].body)

    def test_invite_email(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        self.assertEqual(len(mail.outbox), 0)

        class FakeRequest(object):
            def build_absolute_uri(self, location):
                return 'http://example.com{}'.format(location)

        invite.send_invite_notification(FakeRequest())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['testuser2@example.com'])
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Project group invite for duck1010.active.assignment1')
        self.assertIn(
            u'testuser1 invited you to join their project\ngroup for duck1010 assignment1.',
            mail.outbox[0].body)
        self.assertIn(
            'http://example.com{}'.format(reverse('devilry_student_groupinvite_show',
                kwargs={'invite_id': invite.id})),
            mail.outbox[0].body)