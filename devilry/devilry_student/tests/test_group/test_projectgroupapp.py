import unittest
import mock

from django_cradmin.crinstance import reverse_cradmin_url

from django.test import TestCase
from django.contrib import messages
from django.core.urlresolvers import reverse
import htmls
from django.http import Http404
from django.utils.timezone import datetime, timedelta

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_student.views.group.projectgroupapp import ProjectGroupOverviewView
from devilry.project.develop.testhelpers.soupselect import cssExists
from model_mommy import mommy
from devilry.apps.core.models import GroupInvite
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from django_cradmin import cradmin_testhelpers


class TestProjectGroupOverviewView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = ProjectGroupOverviewView

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

    def test_group_members_table(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        core_mommy.candidate(group=group, fullname="Dewey Duck", shortname="dewey@example.com")
        core_mommy.candidate(group=group, fullname="Huey Duck", shortname="huey@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        self.assertTrue(mockresponse.selector.exists('.table.table-striped.table-bordered'))
        self.assertTrue(mockresponse.selector.exists('#devilry_student_projectgroup_overview_already_in_group'))

    def test_group_project_members_list_fullname(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = core_mommy.candidate(group=group, fullname="April Duck", shortname="april@example.com")
        core_mommy.candidate(group=group, fullname="Dewey Duck", shortname="dewey@example.com")
        core_mommy.candidate(group=group, fullname="Huey Duck", shortname="huey@example.com")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group, requestuser=candidate.relatedstudent.user)
        candidate_list = [cand.alltext_normalized
                          for cand in mockresponse.selector.list('.devilry-student-projectgroupoverview-fullname')]
        self.assertEqual(3, len(candidate_list))
        self.assertIn('April Duck', candidate_list)
        self.assertIn('Dewey Duck', candidate_list)
        self.assertIn('Huey Duck', candidate_list)

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
    viewclass = ProjectGroupOverviewView

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
                           parentnode__students_can_not_create_groups_after=datetime.now() - timedelta(days=10))
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
        messagesmock = mock.MagicMock()
        self.mock_http200_postrequest_htmls(
            requestuser=candidate.relatedstudent.user,
            cradmin_role=group,
            messagesmock=messagesmock,
            requestkwargs={
                'data': {'sent_to': candidate1.id}
            }
        )
        self.assertFalse(GroupInvite.objects.filter(group=group, sent_to=candidate1.relatedstudent.user).exists())


class TestProjectGroupOverviewViewStudentsCanCreateGroups(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = ProjectGroupOverviewView

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
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment)
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
        self.assertNotIn(candidate.relatedstudent.user.get_full_name(), selectlist)
        self.assertIn(candidate1.relatedstudent.user.get_full_name(), selectlist)
        self.assertIn(candidate2.relatedstudent.user.get_full_name(), selectlist)

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
        self.assertIn(candidate.relatedstudent.user.get_full_name(), selectlist)
        self.assertIn(candidate3.relatedstudent.user.get_full_name(), selectlist)
        self.assertNotIn(candidate1.relatedstudent.user.get_full_name(), selectlist)
        self.assertNotIn(candidate2.relatedstudent.user.get_full_name(), selectlist)

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


@unittest.skip('Need updates for new student UI')
class TestGroupInviteRespondView(TestCase):
    def setUp(self):
        self.testfromuser = UserBuilder('testfromuser').user
        self.testtouser = UserBuilder('testtouser').user

    def _getas(self, id, user, *args, **kwargs):
        self.client.login(username=user.shortname, password='test')
        url = reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': id})
        return self.client.get(url, *args, **kwargs)

    def _postas(self, id, user, *args, **kwargs):
        self.client.login(username=user.shortname, password='test')
        url = reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': id})
        return self.client.post(url, *args, **kwargs)

    def test_render(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(invite.id, self.testtouser)
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.one('.page-header h1').alltext_normalized, 'Respond to group invite')
        self.assertEquals(selector.one('.page-header p').alltext_normalized, 'assignment1 - duck1010 - active')

    def test_only_if_invited(self):
        notalloweduser = UserBuilder('notalloweduser').user
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(invite.id, notalloweduser)
        self.assertEquals(response.status_code, 404)

    def test_post_accept(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testfromuser, self.testtouser)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)

        response = self._postas(invite.id, self.testtouser, {
            'accept_invite': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        invite = GroupInvite.objects.get(id=invite.id)
        self.assertTrue(invite.accepted)

    def test_post_decline(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testfromuser, self.testtouser)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)

        response = self._postas(invite.id, self.testtouser, {})
        self.assertEquals(response.status_code, 302)
        invite = GroupInvite.objects.get(id=invite.id)
        self.assertFalse(invite.accepted)

    def test_post_not_allowed(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testfromuser, self.testtouser)\
            .add_assignment('assignment1', students_can_create_groups=False)\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)

        response = self._postas(invite.id, self.testtouser, {})
        self.assertEquals(response.status_code, 200)
        self.assertIn(
            'This assignment does not allow students to form project groups on their own.',
            response.content)
        invite = GroupInvite.objects.get(id=invite.id)
        self.assertEquals(invite.accepted, None)


@unittest.skip('Need updates for new student UI')
class TestGroupInviteDeleteView(TestCase):
    def setUp(self):
        self.testfromuser = UserBuilder('testfromuser').user
        self.testtouser = UserBuilder('testtouser').user

    def _getas(self, group_id, invite_id, user, *args, **kwargs):
        self.client.login(username=user.shortname, password='test')
        url = reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='projectgroup',
            roleid=group_id,
            viewname='delete',
            kwargs={'invite_id': invite_id}
        )
        return self.client.get(url, *args, **kwargs)

    def _postas(self, group_id, invite_id, user, *args, **kwargs):
        self.client.login(username=user.shortname, password='test')
        url = reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='projectgroup',
            roleid=group_id,
            viewname='delete',
            kwargs={'invite_id': invite_id}
        )
        return self.client.post(url, *args, **kwargs)

    def test_render(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        invite = groupbuilder.group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(groupbuilder.group.id, invite.id, self.testfromuser)
        self.assertEquals(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEquals(selector.one('.django-cradmin-page-header-inner h1').alltext_normalized, 'Delete group invite')
        self.assertEquals(selector.one('.django-cradmin-page-header-inner p').alltext_normalized, 'assignment1 - duck1010 - active')

    def test_get_only_if_sender(self):
        notalloweduser = UserBuilder('notalloweduser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        invite = groupbuilder.group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(groupbuilder.group.id, invite.id, notalloweduser)
        self.assertEquals(response.status_code, 404)

    def test_post_only_if_sender(self):
        notalloweduser = UserBuilder('notalloweduser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        invite = groupbuilder.group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._postas(groupbuilder.group.id, invite.id, notalloweduser)
        self.assertEquals(response.status_code, 404)
        self.assertTrue(GroupInvite.objects.filter(id=invite.id).exists())

    def test_post_ok(self):
        notalloweduser = UserBuilder('notalloweduser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        invite = groupbuilder.group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._postas(groupbuilder.group.id, invite.id, self.testfromuser)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(GroupInvite.objects.filter(id=invite.id).exists())
