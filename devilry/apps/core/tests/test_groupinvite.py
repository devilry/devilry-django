from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import timedelta
from django.urls import reverse
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories as core_baker
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import GroupInvite
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_message.models import Message, MessageReceiver


class TestGroupInviteErrors(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_user_sending_is_not_part_of_the_group(self):
        testgroup = baker.make('core.AssignmentGroup')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup1).relatedstudent.user
        sent_to = core_baker.candidate(testgroup2).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The user sending an invite must be a Candiate on the group.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_already_member_of_the_group(self):
        testgroup = baker.make('core.AssignmentGroup')
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The student is already a member of the group.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_already_invited_but_not_responded(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        baker.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to)

        with self.assertRaisesMessage(
                ValidationError,
                'The student is already invited to join the group, but they have not responded yet.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_create_groups_expired(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__students_can_create_groups=True,
                               parentnode__students_can_not_create_groups_after=timezone.now() - timedelta(days=1))
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'Creating project groups without administrator approval is not '
                'allowed on this assignment anymore. Please contact you course '
                'administrator if you think this is wrong.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_assignment_does_not_allow_students_to_form_groups(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__students_can_create_groups=False)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'This assignment does not allow students to form project groups on their own.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_sent_to_is_not_registerd_on_assignment(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup')
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user

        with self.assertRaisesMessage(
                ValidationError,
                'The invited student is not registered on this assignment.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to
            )
            invite.full_clean()

    def test_student_sent_to_is_already_in_a_group_with_more_than_one_student(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        core_baker.candidate(testgroup1)

        with self.assertRaisesMessage(
                ValidationError,
                'The invited student is already in a project group with more than 1 students.'):
            invite = baker.make(
                'core.GroupInvite',
                group=testgroup,
                sent_by=sent_by,
                sent_to=sent_to,
                accepted=True
            )
            invite.full_clean()

    def test_sanity(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        invite = baker.make(
            'core.GroupInvite',
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
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        invite = baker.make(
            'core.GroupInvite',
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
        baker.make('core.GroupInvite', id=100)
        self.assertEqual(GroupInvite.objects.all().first().id, 100)

    def test_filter_accepted(self):
        baker.make('core.GroupInvite', accepted=None, id=10)
        baker.make('core.GroupInvite', accepted=False, id=11)
        baker.make('core.GroupInvite', accepted=True, id=100)
        baker.make('core.GroupInvite', accepted=True, id=101)
        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_accepted()),
            {100, 101}
        )

    def test_filter_no_response(self):
        baker.make('core.GroupInvite', accepted=None, id=10)
        baker.make('core.GroupInvite', accepted=None, id=11)
        baker.make('core.GroupInvite', accepted=True, id=100)
        baker.make('core.GroupInvite', accepted=False, id=101)
        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_no_response()),
            {10, 11}
        )

    def test_filter_rejected(self):
        baker.make('core.GroupInvite', accepted=False, id=10)
        baker.make('core.GroupInvite', accepted=False, id=11)
        baker.make('core.GroupInvite', accepted=True, id=100)
        baker.make('core.GroupInvite', accepted=None, id=101)
        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_rejected()),
            {10, 11}
        )

    def test_filter_unanswered_received_invites(self):
        group = baker.make('core.AssignmentGroup')
        sent_by = core_baker.candidate(group=group).relatedstudent.user
        sent_to = core_baker.candidate(group=group).relatedstudent.user
        baker.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=False, id=10)
        baker.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=None, id=11)
        baker.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=True, id=100)
        baker.make('core.GroupInvite', sent_by=sent_by, sent_to=sent_to, accepted=None, id=101)

        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_unanswered_received_invites(sent_to)),
            {11, 101}
        )

    def test_filter_unanswered_sent_invites(self):
        group = baker.make('core.AssignmentGroup')
        baker.make('core.GroupInvite', group=group, accepted=False, id=10)
        baker.make('core.GroupInvite', group=group, accepted=None, id=11)
        baker.make('core.GroupInvite', group=group, accepted=True, id=100)
        baker.make('core.GroupInvite', group=group, accepted=None, id=101)
        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_unanswered_sent_invites(group)),
            {11, 101}
        )

    def test_filter_allowed_to_create_groups(self):
        assignment_expired = baker.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=timezone.now() - timedelta(days=1)
        )
        assignment_not_expired = baker.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=timezone.now() + timedelta(days=1)
        )
        assignment_not_allowed = baker.make('core.Assignment', students_can_create_groups=False)
        assignment_allowed = baker.make('core.Assignment', students_can_create_groups=True)

        group1 = baker.make('core.AssignmentGroup', parentnode=assignment_expired)
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment_not_expired)
        group3 = baker.make('core.AssignmentGroup', parentnode=assignment_not_allowed)
        group4 = baker.make('core.AssignmentGroup', parentnode=assignment_allowed)

        baker.make('core.GroupInvite', group=group1, id=10)
        baker.make('core.GroupInvite', group=group2, id=11)
        baker.make('core.GroupInvite', group=group3, id=100)
        baker.make('core.GroupInvite', group=group4, id=101)
        self.assertEqual(
            set(invite.id for invite in GroupInvite.objects.filter_allowed_to_create_groups()),
            {11, 101}
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
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_baker.candidate(group=group1).relatedstudent.user
        student2 = core_baker.candidate(group=group2).relatedstudent.user
        invite = baker.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        invite.respond(False)
        self.assertFalse(GroupInvite.objects.get(id=invite.id).accepted)
        group = AssignmentGroup.objects.filter_user_is_candidate(student2)
        self.assertEqual(group.count(), 1)
        self.assertEqual(group.first().id, group2.id)

    def test_respond_accept(self):
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_baker.candidate(group=group1).relatedstudent.user
        student2 = core_baker.candidate(group=group2).relatedstudent.user
        invite = baker.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        invite.respond(True)
        self.assertTrue(GroupInvite.objects.get(id=invite.id).accepted)
        group = AssignmentGroup.objects.filter_user_is_candidate(student2)
        self.assertEqual(group.count(), 1)
        self.assertEqual(group.first().id, group1.id)
        self.assertEqual(group.first().cached_data.candidate_count, 2)
        self.assertFalse(AssignmentGroup.objects.filter(id=group2.id).exists())

    def test_num_queries_accept(self):
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_baker.candidate(group=group1).relatedstudent.user
        student2 = core_baker.candidate(group=group2).relatedstudent.user
        invite = baker.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        with self.assertNumQueries(45):
            invite.respond(True)

    def test_num_queries_reject(self):
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        student1 = core_baker.candidate(group=group1).relatedstudent.user
        student2 = core_baker.candidate(group=group2).relatedstudent.user
        invite = baker.make('core.GroupInvite', sent_by=student1, sent_to=student2, group=group1)
        with self.assertNumQueries(17):
            invite.respond(False)

    def test_send_invite_mail(self):
        assignment = baker.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_baker.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_baker.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        baker.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
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

        message = Message.objects.get()
        message_receiver = MessageReceiver.objects.get()
        self.assertIsNone(message.created_by)
        self.assertEqual(message.context_type, Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_INVITATION.value)
        self.assertDictEqual(message.metadata, {
            'groupinvite_id': invite.id,
            'sent_by_user_id': invite.sent_by.id,
            'sent_to_user_id': invite.sent_to.id
        })
        self.assertEqual(message_receiver.user, invite.sent_to)
        self.assertEqual(message_receiver.subject, 'Project group invite for Duck1010.s17.assignment1')
        self.assertIn(
            f'{ invite.sent_by.get_displayname() } invited you to join their project group',
            message_receiver.message_content_plain
        )
        self.assertIn(testgroup.parentnode.long_name, message_receiver.message_content_plain)
        self.assertIn(testgroup.parentnode.parentnode.parentnode.long_name, message_receiver.message_content_plain.replace('\n', ' '))

    def test_send_reject_mail(self):
        assignment = baker.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_baker.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_baker.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        baker.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
        baker.make('devilry_account.UserEmail', user=sent_by, email="april@example.com")
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

        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageReceiver.objects.count(), 2)
        message = Message.objects.get(context_type=Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_REJECTED.value)
        message_receiver = MessageReceiver.objects.get(message=message)
        self.assertIsNone(message.created_by)
        self.assertDictEqual(message.metadata, {
            'groupinvite_id': invite.id,
            'sent_by_user_id': invite.sent_by.id,
            'sent_to_user_id': invite.sent_to.id
        })
        self.assertEqual(message_receiver.user, invite.sent_by)
        self.assertEqual(message_receiver.subject, f'{invite.sent_to.get_full_name()} rejected your project group invite')
        self.assertIn(
            f'{ invite.sent_to.get_displayname() } rejected the invite to join your project group',
            message_receiver.message_content_plain
        )
        self.assertIn(testgroup.parentnode.long_name, message_receiver.message_content_plain)
        self.assertIn(testgroup.parentnode.parentnode.parentnode.long_name, message_receiver.message_content_plain)

    def test_send_accept_mail(self):
        assignment = baker.make(
            'core.Assignment',
            long_name='Assignment 1',
            short_name='assignment1',
            parentnode__long_name='Spring2017',
            parentnode__short_name='s17',
            parentnode__parentnode__long_name='DUCK1010 - Object Oriented Programming',
            parentnode__parentnode__short_name='Duck1010',
            students_can_create_groups=True,
        )
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        sent_by = core_baker.candidate(testgroup, shortname="april@example.com", fullname="April").relatedstudent.user
        sent_to = core_baker.candidate(testgroup1, shortname="dewey@example.com", fullname="Dewey").relatedstudent.user
        baker.make('devilry_account.UserEmail', user=sent_to, email="dewey@example.com")
        baker.make('devilry_account.UserEmail', user=sent_by, email="april@example.com")
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

        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageReceiver.objects.count(), 2)
        message = Message.objects.get(context_type=Message.CONTEXT_TYPE_CHOICES.GROUP_INVITE_ACCEPTED.value)
        message_receiver = MessageReceiver.objects.get(message=message)
        self.assertIsNone(message.created_by)
        self.assertDictEqual(message.metadata, {
            'groupinvite_id': invite.id,
            'sent_by_user_id': invite.sent_by.id,
            'sent_to_user_id': invite.sent_to.id
        })
        self.assertEqual(message_receiver.user, invite.sent_by)
        self.assertEqual(message_receiver.subject, f'{invite.sent_to.get_full_name()} accepted your project group invite')
        self.assertIn(
            f'{ invite.sent_to.get_displayname() } accepted the invite to join your project group',
            message_receiver.message_content_plain
        )
        self.assertIn(testgroup.parentnode.long_name, message_receiver.message_content_plain)
        self.assertIn(testgroup.parentnode.parentnode.parentnode.long_name, message_receiver.message_content_plain)

    def test_send_invite_to_choices_queryset(self):
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group3 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group4 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        core_baker.candidate(group=group1, fullname="Louie", shortname="louie")
        core_baker.candidate(group=group2, fullname="Huey", shortname="huey")
        core_baker.candidate(group=group2, fullname="Donald", shortname="donald")
        candidate4 = core_baker.candidate(group=group3, fullname="April", shortname="april")
        candidate5 = core_baker.candidate(group=group4, fullname="Dewey", shortname="dewey")
        candidates = GroupInvite.send_invite_to_choices_queryset(group1)
        self.assertEqual(candidates.count(), 2)
        self.assertEqual(
            set(candidate.id for candidate in candidates),
            {candidate4.id, candidate5.id}
        )

    def test_send_invite_to_choices_queryset_pending_is_excluded(self):
        group1 = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        group2 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group3 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        group4 = baker.make('core.AssignmentGroup', parentnode=group1.parentnode)
        candidate1 = core_baker.candidate(group=group1, fullname="Louie", shortname="louie")
        core_baker.candidate(group=group2, fullname="Huey", shortname="huey")
        core_baker.candidate(group=group2, fullname="Donald", shortname="donald")
        candidate4 = core_baker.candidate(group=group3, fullname="April", shortname="april")
        candidate5 = core_baker.candidate(group=group4, fullname="Dewey", shortname="dewey")
        baker.make(
            'core.GroupInvite',
            group=group1,
            sent_to=candidate4.relatedstudent.user,
            sent_by=candidate1.relatedstudent.user
        )
        candidates = GroupInvite.send_invite_to_choices_queryset(group1)
        self.assertEqual(candidates.count(), 1)
        self.assertEqual(
            set(candidate.id for candidate in candidates),
            {candidate5.id}
        )

    def test_validate_user_id_send_to(self):
        assignment = baker.make('core.Assignment', students_can_create_groups=True)
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        core_baker.candidate(testgroup)
        sent_to = core_baker.candidate(testgroup1)
        with self.assertNumQueries(1):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_validation_user_id_send_to_error_wrong_assignment(self):
        assignment = baker.make('core.Assignment', students_can_create_groups=True)
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        testgroup1 = baker.make('core.AssignmentGroup')
        core_baker.candidate(testgroup)
        sent_to = core_baker.candidate(testgroup1)
        with self.assertRaisesMessage(ValidationError, 'The selected student is not eligible to join the group.'):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_validation_user_id_send_to_error_already_in_group(self):
        assignment = baker.make('core.Assignment', students_can_create_groups=True)
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        core_baker.candidate(testgroup)
        sent_to = core_baker.candidate(testgroup)
        with self.assertRaisesMessage(ValidationError, 'The selected student is not eligible to join the group.'):
            GroupInvite.validate_candidate_id_sent_to(testgroup, sent_to.id)

    def test_invite_has_already_been_accepted(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        invite = baker.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to, accepted=True)
        with self.assertRaisesMessage(ValidationError, 'This invite has already been accepted.'):
            invite.respond(True)

    def test_invite_has_already_been_declined(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__students_can_create_groups=True)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testgroup.parentnode)
        sent_by = core_baker.candidate(testgroup).relatedstudent.user
        sent_to = core_baker.candidate(testgroup1).relatedstudent.user
        invite = baker.make('core.GroupInvite', group=testgroup, sent_by=sent_by, sent_to=sent_to, accepted=False)
        with self.assertRaisesMessage(ValidationError, 'This invite has already been declined.'):
            invite.respond(False)
