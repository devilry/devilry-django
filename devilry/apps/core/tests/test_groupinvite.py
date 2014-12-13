from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder
from devilry.apps.core.models import GroupInvite
from devilry.apps.core.models import AssignmentGroup


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
            .add_relatedstudents(self.testuser1)\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The student is already a member of the group.*$'):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser1).clean()

    def test_can_not_invite_someone_that_already_has_invite_for_group(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1',
                students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser2).save()
        with self.assertRaisesRegexp(ValidationError,
                r'^.*The student is already invited to join the group, but they have not responded yet.*$'):
            GroupInvite(group=group, sent_by=self.testuser1, sent_to=self.testuser2).clean()

    def test_can_not_invite_someone_that_is_already_in_projectgroup(self):
        periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)
        assignment1builder = periodbuilder.add_assignment('assignment1',
                students_can_create_groups=True)
        assignment2builder = periodbuilder.add_assignment('assignment2',
                students_can_create_groups=True)

        assignment1builder.add_group(students=[self.testuser2, self.testuser3]).group
        group1 = assignment1builder.add_group(students=[self.testuser1]).group
        group2 = assignment2builder.add_group(students=[self.testuser1]).group

        with self.assertRaisesRegexp(ValidationError,
                r'^.*The invited student is already in a project group.*$'):
            GroupInvite(group=group1, sent_by=self.testuser1, sent_to=self.testuser2,
                accepted=True).clean()

        # Ensure we are not affected by having groups in other assignments
        GroupInvite(group=group2, sent_by=self.testuser1, sent_to=self.testuser2,
                accepted=True).clean()

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

    def test_respond_reject(self):
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
        invite.respond(accepted=False)
        after = datetime.now()
        self.assertFalse(invite.accepted)
        self.assertTrue(invite.responded_datetime >= before and invite.responded_datetime <= after)
        self.assertTrue(group.candidates.count(), 1)

    def test_respond_accept_merge_groups(self):
        assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)
        group = assignmentbuilder.add_group(students=[self.testuser1]).group
        sent_to_group = assignmentbuilder.add_group(students=[self.testuser2]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        invite.save()
        self.assertEquals(AssignmentGroup.objects.count(), 2)
        invite.respond(accepted=True)
        self.assertTrue(invite.accepted)
        self.assertTrue(group.candidates.count(), 2)
        self.assertEquals(set([c.student for c in group.candidates.all()]),
            set([self.testuser1, self.testuser2]))
        self.assertEquals(AssignmentGroup.objects.count(), 1)
        self.assertFalse(AssignmentGroup.objects.filter(id=sent_to_group.id).exists())

    def test_respond_accept_add_candidate(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser1]).group
        invite = GroupInvite(
            group=group,
            sent_by=self.testuser1,
            sent_to=self.testuser2)
        invite.save()
        self.assertEquals(AssignmentGroup.objects.count(), 1)
        invite.respond(accepted=True)
        self.assertTrue(invite.accepted)
        self.assertTrue(group.candidates.count(), 2)
        self.assertEquals(set([c.student for c in group.candidates.all()]),
            set([self.testuser1, self.testuser2]))
        self.assertEquals(AssignmentGroup.objects.count(), 1)

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
            'http://example.com{}'.format(reverse('devilry_student_groupinvite_respond',
                kwargs={'invite_id': invite.id})),
            mail.outbox[0].body)


    def test_send_invite_to_choices_queryset(self):
        UserBuilder('ignoreduser')
        alreadyingroupuser1 = UserBuilder('alreadyingroupuser1').user
        alreadyingroupuser2 = UserBuilder('alreadyingroupuser2').user
        hasinviteuser = UserBuilder('hasinviteuser').user
        matchuser1 = UserBuilder('matchuser1').user
        matchuser2 = UserBuilder('matchuser2').user

        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(
                alreadyingroupuser1, alreadyingroupuser2, hasinviteuser,
                matchuser1, matchuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[alreadyingroupuser1, alreadyingroupuser2]).group
        group.groupinvite_set.create(
            sent_by=alreadyingroupuser1,
            sent_to=hasinviteuser)

        can_invite_users = set(GroupInvite.send_invite_to_choices_queryset(group))
        self.assertEquals(can_invite_users, set([matchuser1, matchuser2]))
