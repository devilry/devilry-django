from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import datetime, timedelta
from django.core.urlresolvers import reverse
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import GroupInvite
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestGroupInviteErrors(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_user_sending_is_not_part_of_the_group(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup1).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup2).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The user sending an invite must be a Candiate on the group.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_already_member_of_the_group(self):
        testgroup = mommy.make('core.AssignmentGroup')
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The student is already a member of the group.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_already_invited_but_not_responded(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        mommy.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to)

        with self.assertRaisesMessage(
                ValidationError,
                'The student is already invited to join the group, but they have not responded yet.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_create_groups_expired(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_create_groups=True,
                               parentnode__students_can_not_create_groups_after=datetime.now() - timedelta(days=1))
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'Creating project groups without administrator approval is not '
                'allowed on this assignment anymore. Please contact you course '
                'administrator if you think this is wrong.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_assignment_does_not_allow_students_to_form_groups(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__students_can_create_groups=False)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'This assignment does not allow students to form project groups on their own.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_sent_to_is_not_registerd_on_assignment(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup')
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The invited student is not registered on this assignment.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_sent_to_is_already_in_a_group_with_more_than_one_student(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        core_mommy.candidate(testgroup1)

        with self.assertRaisesMessage(
                ValidationError,
                'The invited student is already in a project group with more than 1 students.'):
            invite = GroupInvite(
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to,
                accepted=True
            )
            invite.full_clean()

    def test_sanity(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        invite = GroupInvite(
            group=testgroup,
            sent_by=sent_by,
            sent_to=sent_to
        )
        invite.full_clean()
        self.assertEqual(invite.sent_to, sent_to)
        self.assertEqual(invite.sent_by, sent_by)
        self.assertEqual(invite.group, testgroup)
        self.assertIsNotNone(invite.sent_datetime)

    def test_sanity_accepted(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        invite = GroupInvite(
            group=testgroup,
            sent_by=sent_by,
            sent_to=sent_to,
            accepted=True
        )
        invite.full_clean()
        self.assertEqual(invite.sent_to, sent_to)
        self.assertEqual(invite.sent_by, sent_by)
        self.assertEqual(invite.group, testgroup)
        self.assertTrue(invite.accepted)
        self.assertIsNotNone(invite.responded_datetime)


class TestGroupInviteQueryset(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_queryset_sanity(self):
        mommy.make('core.GroupInvite', id=100)
        self.assertEqual(GroupInvite.objects.all().first().id, 100)

    def test_filter_accepted(self):
        mommy.make('core.GroupInvite', accepted=None, id=10)
        mommy.make('core.GroupInvite', accepted=False, id=11)
        mommy.make('core.GroupInvite', accepted=True, id=100)
        mommy.make('core.GroupInvite', accepted=True, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_accepted()],
            [100, 101]
        )

    def test_filter_no_response(self):
        mommy.make('core.GroupInvite', accepted=None, id=10)
        mommy.make('core.GroupInvite', accepted=None, id=11)
        mommy.make('core.GroupInvite', accepted=True, id=100)
        mommy.make('core.GroupInvite', accepted=False, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_no_response()],
            [10, 11]
        )

    def test_filter_rejected(self):
        mommy.make('core.GroupInvite', accepted=False, id=10)
        mommy.make('core.GroupInvite', accepted=False, id=11)
        mommy.make('core.GroupInvite', accepted=True, id=100)
        mommy.make('core.GroupInvite', accepted=None, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_rejected()],
            [10, 11]
        )

    def test_filter_unanswered_received_invites(self):
        group = mommy.make('core.AssignmentGroup')
        sent_by = core_mommy.candidate(group=group).relatedstudent.user
        sent_to = core_mommy.candidate(group=group).relatedstudent.user
        mommy.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=False, id=10)
        mommy.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=None, id=11)
        mommy.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=True, id=100)
        mommy.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=None, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_unanswered_received_invites(sent_to)],
            [11, 101]
        )

    def test_filter_unanswered_sent_invites(self):
        group = mommy.make('core.AssignmentGroup')
        mommy.make('core.GroupInvite', group=group, accepted=False, id=10)
        mommy.make('core.GroupInvite', group=group, accepted=None, id=11)
        mommy.make('core.GroupInvite', group=group, accepted=True, id=100)
        mommy.make('core.GroupInvite', group=group, accepted=None, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_unanswered_sent_invites(group)],
            [11, 101]
        )

    def test_filter_allowed_to_create_groups(self):
        assignment_expired = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=datetime.now() - timedelta(days=1)
        )
        assignment_not_expired = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=datetime.now() + timedelta(days=1)
        )
        assignment_not_allowed = mommy.make('core.Assignment', students_can_create_groups=False)
        assignment_allowed = mommy.make('core.Assignment', students_can_create_groups=True)

        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment_expired)
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment_not_expired)
        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment_not_allowed)
        group4 = mommy.make('core.AssignmentGroup', parentnode=assignment_allowed)

        mommy.make('core.GroupInvite', group=group1, id=10)
        mommy.make('core.GroupInvite', group=group2, id=11)
        mommy.make('core.GroupInvite', group=group3, id=100)
        mommy.make('core.GroupInvite', group=group4, id=101)
        self.assertListEqual(
            [invite.id for invite in GroupInvite.objects.filter_allowed_to_create_groups()],
            [11, 101]
        )


class FakeRequest(object):
    def build_absolute_uri(self, location):
        return 'http://example.com{}'.format(location)


class GroupInviteRespond(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __fake_request(self):
        return FakeRequest()

    def test_respond_reject(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_mommy.candidate(group=group1).relatedstudent.user
        student2 = core_mommy.candidate(group=group2).relatedstudent.user
        invite = mommy.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        invite.respond(False)
        self.assertFalse(GroupInvite.objects.get(id=invite.id).accepted)
        group = AssignmentGroup.objects.filter_user_is_candidate(student2)
        self.assertEqual(group.count(), 1)
        self.assertEqual(group.first().id, group2.id)

    def test_respond_accept(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_mommy.candidate(group=group1).relatedstudent.user
        student2 = core_mommy.candidate(group=group2).relatedstudent.user
        invite = mommy.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        invite.respond(True)
        self.assertTrue(GroupInvite.objects.get(id=invite.id).accepted)
        group = AssignmentGroup.objects.filter_user_is_candidate(student2)
        self.assertEqual(group.count(), 1)
        self.assertEqual(group.first().id, group1.id)
        self.assertEqual(group.first().cached_data.candidate_count, 2)
        self.assertFalse(AssignmentGroup.objects.filter(id=group2.id).exists())

    def test_num_queries_accept(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_mommy.candidate(group=group1).relatedstudent.user
        student2 = core_mommy.candidate(group=group2).relatedstudent.user
        invite = mommy.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        with self.assertNumQueries(32):
            invite.respond(True)

    def test_num_queries_reject(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_mommy.candidate(group=group1).relatedstudent.user
        student2 = core_mommy.candidate(group=group2).relatedstudent.user
        invite = mommy.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        with self.assertNumQueries(9):
            invite.respond(False)

    def test_send_invite_mail(self):
        assignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_mommy.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        mommy.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
        invite = GroupInvite(group=testgroup, sent_by=sent_by, sent_to=sent_to)
        invite.full_clean()
        invite.save()
        request = self.__fake_request()
        invite.send_invite_notification(request)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Project group invite for Duck1010.s17.assignment1')
        url = request.build_absolute_uri(
            reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': invite.id}))
        self.assertIn(url, mail.outbox[0].body)

    def test_send_reject_mail(self):
        assignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_mommy.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        mommy.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
        mommy.make('devilry_account.UserEmail', user=sent_by, email="april@example.com")
        invite = GroupInvite(
            group=testgroup,
            sent_by=sent_by,
            sent_to=sent_to
        )
        invite.full_clean()
        invite.save()
        invite.send_invite_notification(self.__fake_request())
        invite.respond(False)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, '[Devilry] Dewey rejected your project group invite')

    def test_send_accept_mail(self):
        assignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_mommy.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        mommy.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
        mommy.make('devilry_account.UserEmail', user=sent_by, email="april@example.com")
        invite = GroupInvite(
            group=testgroup,
            sent_by=sent_by,
            sent_to=sent_to
        )
        invite.full_clean()
        invite.save()
        invite.send_invite_notification(self.__fake_request())
        invite.respond(True)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, '[Devilry] Dewey accepted your project group invite')

    def test_send_invite_to_choices_queryset(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group3 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group4 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        core_mommy.candidate(group=group1, fullname="Louie", shortname="louie")
        core_mommy.candidate(group=group2, fullname="Huey", shortname="huey")
        core_mommy.candidate(group=group2, fullname="Donald", shortname="donald")
        candidate4 = core_mommy.candidate(group=group3, fullname="April", shortname="april")
        candidate5 = core_mommy.candidate(group=group4, fullname="Dewey", shortname="dewey")
        candidates = GroupInvite.send_invite_to_choices_queryset(group1)
        self.assertEqual(candidates.count(), 2)
        self.assertListEqual(
            [candidate for candidate in candidates],
            [candidate4, candidate5]
        )

    def test_send_invite_to_choices_queryset_pending_is_excluded(self):
        group1 = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group3 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group4 = mommy.make('core.AssignmentGroup', parentnode=group1.parentnode)
        candidate1 = core_mommy.candidate(group=group1, fullname="Louie", shortname="louie")
        core_mommy.candidate(group=group2, fullname="Huey", shortname="huey")
        core_mommy.candidate(group=group2, fullname="Donald", shortname="donald")
        candidate4 = core_mommy.candidate(group=group3, fullname="April", shortname="april")
        candidate5 = core_mommy.candidate(group=group4, fullname="Dewey", shortname="dewey")
        mommy.make(
            'core.GroupInvite',
            group=group1,
            sent_to=candidate4.relatedstudent.user,
            sent_by=candidate1.relatedstudent.user
        )
        candidates = GroupInvite.send_invite_to_choices_queryset(group1)
        self.assertEqual(candidates.count(), 1)
        self.assertListEqual(
            [candidate for candidate in candidates],
            [candidate5]
        )

    def test_validate_user_id_send_to(self):
        assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        core_mommy.candidate(testgroup)
        sent_to = core_mommy.candidate(testgroup1)
        with self.assertNumQueries(1):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_validation_user_id_send_to_error_wrong_assignment(self):
        assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(testgroup)
        sent_to = core_mommy.candidate(testgroup1)
        with self.assertRaisesMessage(ValidationError, 'The selected student is not eligible to join the group.'):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_validation_user_id_send_to_error_already_in_group(self):
        assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        core_mommy.candidate(testgroup)
        sent_to = core_mommy.candidate(testgroup)
        with self.assertRaisesMessage(ValidationError, 'The selected student is not eligible to join the group.'):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_invite_has_already_been_accepted(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        invite = mommy.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to, accepted=True)
        with self.assertRaisesMessage(ValidationError, 'This invite has already been accepted.'):
            invite.respond(True)

    def test_invite_has_already_been_declined(self):
        testgroup = mommy.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_mommy.candidate(testgroup).relatedstudent.user
        sent_to = core_mommy.candidate(testgroup1).relatedstudent.user
        invite = mommy.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to, accepted=False)
        with self.assertRaisesMessage(ValidationError, 'This invite has already been declined.'):
            invite.respond(False)
