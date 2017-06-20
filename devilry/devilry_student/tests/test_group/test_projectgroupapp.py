import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import GroupInvite
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_student.views.group import projectgroupapp


class TestProjectGroupOverviewView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.ProjectGroupOverviewView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertIn(
            'Project group',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertIn(
            'Project group',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_inner_header_p(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertIn(
            '{} - {} - {}'.format(testassignment.long_name,
                                  testassignment.parentnode.parentnode.long_name,
                                  testassignment.parentnode.long_name),
            mockresponse.selector.one('.django-cradmin-page-header-inner > p').alltext_normalized
        )

    def test_group_members_ul_exists(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        core_mommy.candidate(group=group, fullname="Dewey Duck", shortname="dewey@example.com")
        core_mommy.candidate(group=group, fullname="Huey Duck", shortname="huey@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('#devilry_student_projectgroup_overview_already_in_group > ul'))

    def test_group_project_members_displayname(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group, fullname="Dewey Duck", shortname="dewey@example.com")
        candidate2 = core_mommy.candidate(group=group, fullname="Huey Duck", shortname="huey@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        candidate_list = [
            cand.alltext_normalized
            for cand in mockresponse.selector.list('#devilry_student_projectgroup_overview_already_in_group > ul > li')]
        self.assertEqual(3, len(candidate_list))
        self.assertIn(candidate.relatedstudent.user.get_displayname(), candidate_list)
        self.assertIn(candidate1.relatedstudent.user.get_displayname(), candidate_list)
        self.assertIn(candidate2.relatedstudent.user.get_displayname(), candidate_list)

    def test_links(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertEquals(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='feedbackfeed', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )


class TestProjectGroupOverviewViewStudentsCannotCreateGroups(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.ProjectGroupOverviewView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_submit_button_sutdents_cannot_create_groups(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('#submit-id-submit'))

    def test_submit_button_students_cannot_create_groups_expired(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__students_can_create_groups=True,
                           parentnode__students_can_not_create_groups_after=timezone.now() - timedelta(days=10))
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('#submit-id-submit'))

    def test_invite_box_does_not_exists(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('#devilry_student_projectgroupoverview_invitebox'))

    def test_waiting_for_response_form_does_not_exists(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('#devilry_student_projectgroup_overview_waiting_for_response_from'))

    def test_cannot_invite_student_to_group(self):
        test_assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        self.mock_http200_postrequest_htmls(
            requestuser=candidate.relatedstudent.user,
            cradmin_role=group,
            requestkwargs={
                'data': {'sent_to': candidate1.id}
            }
        )
        self.assertFalse(GroupInvite.objects.filter(group=group, sent_to=candidate1.relatedstudent.user).exists())

    def test_received_invite_cannot_create_group(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=False)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.alert.alert-success'))
        self.assertFalse(mockresponse.selector.exists('.btn.btn-default'))

    def test_received_invite_cannot_create_group_expired(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=timezone.now() - timedelta(days=1)
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user)
        self.assertFalse(mockresponse.selector.exists('.alert.alert-success'))
        self.assertFalse(mockresponse.selector.exists('.btn.btn-default'))


class TestProjectGroupOverviewViewStudentsCanCreateGroups(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.ProjectGroupOverviewView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_submit_button_visible_when_students_can_create(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__students_can_create_groups=True)
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-submit'))

    def test_invite_box_exists(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__students_can_create_groups=True)
        candidate = core_mommy.candidate(group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('#devilry_student_projectgroupoverview_invitebox'))

    def test_invite_box_correct_students_is_shown(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Huey Duck", shortname="huey@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('#id_sent_to > option')]
        self.assertNotIn(candidate.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate1.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate2.relatedstudent.user.get_displayname(), selectlist)

    def test_invite_student_to_group(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            requestuser=candidate.relatedstudent.user,
            cradmin_role=group,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {'sent_to': candidate1.id}
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Invite sent to {}.'.format(candidate1.relatedstudent.user.get_displayname()),
            ''
        )

    def test_invite_student_to_group_db(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            requestuser=candidate.relatedstudent.user,
            cradmin_role=group,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {'sent_to': candidate1.id}
            }
        )
        self.assertTrue(GroupInvite.objects.filter(group=group, sent_to=candidate1.relatedstudent.user).exists())

    def test_selected_choice_is_not_valid(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group, fullname="Dewey Duck", shortname="dewey@example.com")
        messagesmock = mock.MagicMock()
        self.mock_http200_postrequest_htmls(
            requestuser=candidate.relatedstudent.user,
            cradmin_role=group,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {'sent_to': candidate1.id}
            }
        )

    def test_waiting_for_response_from_names(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Huey Duck", shortname="huey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate2.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.invite_sent_to_displayname')]
        self.assertNotIn(candidate.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate1.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate2.relatedstudent.user.get_displayname(), selectlist)

    def test_waiting_for_response_from_invited_by(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate3 = core_mommy.candidate(group=group, fullname="Louie Duck", shortname="louie@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Huey Duck", shortname="huey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate3.relatedstudent.user, sent_to=candidate2.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.invited_sent_by_displayname')]
        self.assertIn(candidate.relatedstudent.user.get_displayname(), selectlist)
        self.assertIn(candidate3.relatedstudent.user.get_displayname(), selectlist)
        self.assertNotIn(candidate1.relatedstudent.user.get_displayname(), selectlist)
        self.assertNotIn(candidate2.relatedstudent.user.get_displayname(), selectlist)

    def test_waiting_for_response_delete_button(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Huey Duck", shortname="huey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate2.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertEqual(len(mockresponse.selector.list('.btn.btn-danger.btn-xs')), 2)

    def test_received_invite(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        mommy.make('core.GroupInvite', group=group,
                   sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group1,
                                                          requestuser=candidate1.relatedstudent.user)
        self.assertIn(
            'You have been invited to join a group! {} invited you to join their group.'.format(
                candidate.relatedstudent.user.get_displayname()),
            mockresponse.selector.one('.alert.alert-success').alltext_normalized)
        self.assertIn(
            'More info',
            mockresponse.selector.one('.btn.btn-default').alltext_normalized)

    def test_get_num_queries(self):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__students_can_create_groups=True)
        candidate = core_mommy.candidate(group=group)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)


class TestGroupInviteRespondView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.GroupInviteRespondView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Respond to group invite',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Respond to group invite',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_inner_header_p(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            '{} - {} - {}'.format(testassignment.long_name,
                                  testassignment.parentnode.parentnode.long_name,
                                  testassignment.parentnode.long_name),
            mockresponse.selector.one('.django-cradmin-page-header-inner > .container > p').alltext_normalized
        )

    def test_form_text(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010',
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'You have been invited by {} to join their project group for {} {}.'.format(
                candidate.relatedstudent.user.get_full_name(),
                testassignment.subject.long_name,
                testassignment.long_name
            ),
            mockresponse.selector.one(
                'form > p').alltext_normalized
        )

    def test_decline_button(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010',
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Decline invitation',
            mockresponse.selector.one('.btn.btn-danger').alltext_normalized
        )

    def test_accept_button(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010',
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Accept invitation',
            mockresponse.selector.one('.btn.btn-success').alltext_normalized
        )

    def test_links(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertEquals(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='projectgroup', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_already_part_of_group_with_more_than_one_student(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user)
        core_mommy.candidate(group=group1)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'You are already part of a group with more than one student!',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )

    def test_decline_invitation_message(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            messagesmock=messagesmock,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'decline_invite': ''
                }
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Declined group invitation from {}.'.format(candidate.relatedstudent.user.get_displayname()),
            ''
        )

    def test_decline_invitation_db(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        self.mock_http302_postrequest(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'decline_invite': ''
                }
            }
        )
        self.assertFalse(GroupInvite.objects.get(id=invite.id).accepted)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertEqual(AssignmentGroup.objects.get(id=group.id).cached_data.candidate_count, 1)
        self.assertEqual(AssignmentGroup.objects.get(id=group1.id).cached_data.candidate_count, 1)

    def test_decline_accept_message(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            messagesmock=messagesmock,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Joined the group by invitation from {}.'.format(candidate.relatedstudent.user.get_displayname()),
            ''
        )

    def test_accept_invitation_db(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        self.mock_http302_postrequest(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertTrue(GroupInvite.objects.get(id=invite.id).accepted)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertEqual(AssignmentGroup.objects.get(id=group.id).cached_data.candidate_count, 2)

    def test_accept_allready_part_of_a_group_with_more_than_one_student(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        core_mommy.candidate(group=group1)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group1,
            requestuser=candidate1.relatedstudent.user,
            messagesmock=messagesmock,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.WARNING,
            'The invited student is already in a project group with more than 1 students.',
            ''
        )

    def test_get_404_invite_has_already_been_accepted(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=True)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group1,
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_get_404_invite_has_already_been_declined(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=False)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group1,
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_404_student_can_no_longer_invite(self):
        testassignment = mommy.make('core.Assignment',
                                    students_can_create_groups=True,
                                    students_can_not_create_groups_after=timezone.now() - timedelta(days=1))
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=False)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group1,
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_404_students_cannot_create_groups(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=False)
        testassignment.students_can_create_groups = False
        testassignment.save()
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group1,
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_get_num_queries(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        with self.assertNumQueries(3):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group,
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )


class TestGroupInviteDeleteView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.GroupInviteDeleteView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Delete group invite',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Delete group invite',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_form_text(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Are you sure you want to delete the invite for {}?'.format(invite.sent_to.get_full_name()),
            mockresponse.selector.one('form > p').alltext_normalized
        )

    def test_header_inner_p(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            '{} - {} - {}'.format(
                testassignment.long_name,
                testassignment.subject.long_name,
                testassignment.period.long_name
            ),
            mockresponse.selector.one(
                '.django-cradmin-page-header-inner > p').alltext_normalized
        )

    def test_delete_button(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Delete invite',
            mockresponse.selector.one('.btn.btn-danger').alltext_normalized
        )

    def test_links(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertEquals(2, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='projectgroup', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEqual(
            mock.call(appname='projectgroup', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )

    def test_delete_invitation_message(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group,
            messagesmock=messagesmock,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Removed project group invitation {}.'.format(candidate1.relatedstudent.user.get_displayname()),
            ''
        )

    def test_delete_invitation_db(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group,
            messagesmock=messagesmock,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertFalse(GroupInvite.objects.filter(id=invite.id).exists())

    def test_delete_invitation_by_another_user_in_group_message(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate2 = core_mommy.candidate(group=group, fullname="Donald Duck", shortname="donald@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group,
            messagesmock=messagesmock,
            requestuser=candidate2.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Removed project group invitation {}.'.format(candidate1.relatedstudent.user.get_displayname()),
            ''
        )

    def test_delete_invitation_by_another_user_in_group_db(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate2 = core_mommy.candidate(group=group, fullname="Donald Duck", shortname="donald@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=group,
            messagesmock=messagesmock,
            requestuser=candidate2.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertFalse(GroupInvite.objects.filter(id=invite.id).exists())

    def test_delete_invitation_by_a_user_not_in_group_404(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Donald Duck", shortname="donald@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        with self.assertRaises(Http404):
            self.mock_http302_postrequest(
                cradmin_role=group,
                messagesmock=messagesmock,
                requestuser=candidate2.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_get_invitation_by_a_user_not_in_group_404(self):
        testassignment = mommy.make(
            'core.Assignment',
            long_name='Assignment 1',
            parentnode__long_name='Spring 2017',
            parentnode__parentnode__long_name='Duck1010'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate2 = core_mommy.candidate(group=group2, fullname="Donald Duck", shortname="donald@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group,
                messagesmock=messagesmock,
                requestuser=candidate2.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_get_num_queries(self):
        testassignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(
                cradmin_role=group,
                requestuser=candidate.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )


class TestGroupInviteRespondViewStandalone(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = projectgroupapp.GroupInviteRespondViewStandalone

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Respond to group invite',
            mockresponse.selector.one('title').alltext_normalized)

    def test_page_header_h1(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Respond to group invite',
            mockresponse.selector.one('.page-header > .container > h1').alltext_normalized)

    def test_page_header_p(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            '{} - {} - {}'.format(
                test_assignment.long_name,
                test_assignment.subject.long_name,
                test_assignment.period.long_name
            ),
            mockresponse.selector.one('.page-header > .container > p').alltext_normalized)

    def test_form_text(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'You have been invited by {} to join their project group for {} {}.'.format(
                candidate.relatedstudent.user.get_displayname(),
                test_assignment.subject.long_name,
                test_assignment.long_name),
            mockresponse.selector.one('form').alltext_normalized)

    def test_decline_button(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Decline invitation',
            mockresponse.selector.one('.btn.btn-danger').alltext_normalized
        )

    def test_accept_button(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'Accept invitation',
            mockresponse.selector.one('.btn.btn-success').alltext_normalized
        )

    def test_user_is_not_logged_in(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_404_can_not_view_another_users_invite(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                requestuser=candidate.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_already_in_group_with_more_than_one_student(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        core_mommy.candidate(group=group1, fullname="Donald Duck", shortname="donald@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            }
        )
        self.assertIn(
            'You are already part of a group with more than one student!',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )

    def test_post_already_in_group_with_more_than_one_student(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        core_mommy.candidate(group=group1, fullname="Donald Duck", shortname="donald@example.com")
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=group,
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertIn(
            'You are already part of a group with more than one student!',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertIsNone(GroupInvite.objects.get(id=invite.id).accepted)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertEqual(AssignmentGroup.objects.get(id=group1.id).cached_data.candidate_count, 2)
        self.assertEqual(AssignmentGroup.objects.get(id=group.id).cached_data.candidate_count, 1)

    def test_accept_invitation_message(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            requestuser=candidate1.relatedstudent.user,
            messagesmock=messagesmock,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Joined the group by invitation from {}.'.format(candidate.relatedstudent.user.get_displayname()),
            ''
        )

    def test_accept_invitation_db(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        self.mock_http302_postrequest(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertTrue(GroupInvite.objects.get(id=invite.id).accepted)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertEqual(AssignmentGroup.objects.get(id=group.id).cached_data.candidate_count, 2)

    def test_decline_invitation_message(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            requestuser=candidate1.relatedstudent.user,
            messagesmock=messagesmock,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'decline_invite': ''
                }
            }
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Declined group invitation from {}.'.format(candidate.relatedstudent.user.get_displayname()),
            ''
        )

    def test_decline_invitation_db(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        self.mock_http302_postrequest(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'decline_invite': ''
                }
            }
        )
        self.assertFalse(GroupInvite.objects.get(id=invite.id).accepted)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertEqual(AssignmentGroup.objects.get(id=group.id).cached_data.candidate_count, 1)
        self.assertEqual(AssignmentGroup.objects.get(id=group1.id).cached_data.candidate_count, 1)

    def test_invite_already_accepted_this_invite(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            parentnode__parentnode__long_name='Duck1010',
            parentnode__long_name='Spring 2017',
            long_name='Assignment 1'
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=True)

        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
        )
        self.assertIn(
            'You have already accepted this invite',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_invite_already_declined_this_invite(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user,
                            sent_to=candidate1.relatedstudent.user, accepted=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
        )
        self.assertIn(
            'You have already declined this invite',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_accept_student_can_no_longer_invite(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=timezone.now() - timedelta(days=1)
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertIn(
            'Creating project groups without administrator approval is not '
            'allowed on this assignment anymore. Please contact you course '
            'administrator if you think this is wrong.',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_accept_invite_students_can_not_create_groups(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        test_assignment.students_can_create_groups = False
        test_assignment.save()
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertIn(
            'This assignment does not allow students to form project groups on their own.',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertTrue(AssignmentGroup.objects.filter(id=group1.id).exists())
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_get_student_can_no_longer_invite(self):
        test_assignment = mommy.make(
            'core.Assignment',
            students_can_create_groups=True,
            students_can_not_create_groups_after=timezone.now() - timedelta(days=1)
        )
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertIn(
            'Creating project groups without administrator approval is not '
            'allowed on this assignment anymore. Please contact you course '
            'administrator if you think this is wrong.',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_get_students_can_not_create_groups(self):
        test_assignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)
        test_assignment.students_can_create_groups = False
        test_assignment.save()
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=candidate1.relatedstudent.user,
            viewkwargs={
                'invite_id': invite.id
            },
            requestkwargs={
                'data': {
                    'accept_invite': ''
                }
            }
        )
        self.assertIn(
            'This assignment does not allow students to form project groups on their own.',
            mockresponse.selector.one('.alert.alert-danger').alltext_normalized
        )
        self.assertFalse(mockresponse.selector.exists('form'))

    def test_get_num_queries(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)

        with self.assertNumQueries(3):
            self.mock_http200_getrequest_htmls(
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                }
            )

    def test_post_decline_num_queries(self):
        testassignment = mommy.make('core.Assignment', students_can_create_groups=True)
        group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        candidate1 = core_mommy.candidate(group=group1, fullname="Dewey Duck", shortname="dewey@example.com")
        invite = mommy.make('core.GroupInvite', group=group,
                            sent_by=candidate.relatedstudent.user, sent_to=candidate1.relatedstudent.user)

        with self.assertNumQueries(13):
            self.mock_http302_postrequest(
                requestuser=candidate1.relatedstudent.user,
                viewkwargs={
                    'invite_id': invite.id
                },
                requestkwargs={
                    'data': {
                        'decline_invite': ''
                    }
                }
            )
