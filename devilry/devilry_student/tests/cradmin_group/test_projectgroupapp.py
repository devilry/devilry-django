from django_cradmin.crinstance import reverse_cradmin_url

from django.test import TestCase

from django.core.urlresolvers import reverse
import htmls

from devilry.project.develop.testhelpers.soupselect import cssExists

from devilry.apps.core.models import GroupInvite
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class TestProjectGroupOverviewView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _getas(self, group_id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='projectgroup',
            roleid=group_id
        )
        return self.client.get(url, *args, **kwargs)

    def _postas(self, group_id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='projectgroup',
            roleid=group_id
        )
        return self.client.post(url, *args, **kwargs)

    def test_render(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        response = self._getas(groupbuilder.group.id, self.testuser)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, 'h1').text.strip(), 'Project group')

    def test_groupinvite_not_allowed(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', students_can_create_groups=False)\
            .add_group(students=[self.testuser])
        html = self._getas(groupbuilder.group.id, self.testuser).content
        self.assertFalse(cssExists(html, '#devilry_student_projectgroupoverview_invitebox'))

    def test_groupinvite_allowed(self):
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        html = self._getas(groupbuilder.group.id, self.testuser).content
        self.assertTrue(cssExists(html, '#devilry_student_projectgroupoverview_invitebox'))

    def test_render_send_invite_to_selectlist(self):
        UserBuilder('ignoreduser')
        alreadyingroupuser1 = UserBuilder('alreadyingroupuser1').user
        alreadyingroupuser2 = UserBuilder('alreadyingroupuser2').user
        hasinviteuser = UserBuilder('hasinviteuser').user
        matchuser1 = UserBuilder('matchuser1').user
        matchuser2 = UserBuilder('matchuser2', full_name='Match User Two').user

        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(
                alreadyingroupuser1, alreadyingroupuser2, hasinviteuser,
                matchuser1, matchuser2)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[alreadyingroupuser1, alreadyingroupuser2])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        groupbuilder.group.groupinvite_set.create(
            sent_by=alreadyingroupuser1,
            sent_to=hasinviteuser)

        html = self._getas(groupbuilder.group.id, alreadyingroupuser1).content
        send_to_options = [e.text.strip() for e in cssFind(html, '#id_sent_to option')]
        self.assertEquals(send_to_options, ['', 'matchuser1', 'Match User Two'])

    def test_render_waiting_for_response_from(self):
        inviteuser1 = UserBuilder('inviteuser1').user
        inviteuser2 = UserBuilder('inviteuser2').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        for inviteuser in (inviteuser1, inviteuser2):
            groupbuilder.group.groupinvite_set.create(
                sent_by=self.testuser,
                sent_to=inviteuser)

        html = self._getas(groupbuilder.group.id, self.testuser).content
        names = [element.text.strip() for element in \
            cssFind(html, '#devilry_student_projectgroup_overview_waiting_for_response_from .invite_sent_to_displayname')]
        self.assertEquals(set(names), {'inviteuser1', 'inviteuser2'})

    def test_render_current_group_members(self):
        otheruser = UserBuilder('otheruser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser, otheruser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)

        html = self._getas(groupbuilder.group.id, self.testuser).content
        names = [element.text.strip() for element in \
            cssFind(html, '#devilry_student_projectgroup_overview_already_in_group .groupmember_username')]
        self.assertEquals(set(names), {'testuser', 'otheruser'})

    def test_send_to_post(self):
        inviteuser = UserBuilder('inviteuser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser, inviteuser)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)

        self.assertEquals(GroupInvite.objects.count(), 0)
        response = self._postas(groupbuilder.group.id, self.testuser, {
            'sent_to': inviteuser.id
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(GroupInvite.objects.count(), 1)
        invite = GroupInvite.objects.all()[0]
        self.assertEquals(invite.sent_by, self.testuser)
        self.assertEquals(invite.sent_to, inviteuser)
        self.assertEquals(invite.accepted, None)

    def test_send_to_post_notrelated(self):
        inviteuser = UserBuilder('inviteuser').user
        groupbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_relatedstudents(self.testuser)\
            .add_assignment('assignment1', students_can_create_groups=True)\
            .add_group(students=[self.testuser])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)

        self.assertEquals(GroupInvite.objects.count(), 0)
        response = self._postas(groupbuilder.group.id, self.testuser, {
            'sent_to': inviteuser.id
        })
        self.assertEquals(response.status_code, 200)
        self.assertIn(
            'Select a valid choice. {} is not one of the available choices.'.format(inviteuser.id),
            response.content)


class TestGroupInviteRespondView(TestCase):
    def setUp(self):
        self.testfromuser = UserBuilder('testfromuser').user
        self.testtouser = UserBuilder('testtouser').user

    def _getas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_groupinvite_respond', kwargs={'invite_id': id})
        return self.client.get(url, *args, **kwargs)

    def _postas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
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


class TestGroupInviteDeleteView(TestCase):
    def setUp(self):
        self.testfromuser = UserBuilder('testfromuser').user
        self.testtouser = UserBuilder('testtouser').user

    def _getas(self, group_id, invite_id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='projectgroup',
            roleid=group_id,
            viewname='delete',
            kwargs={'invite_id': invite_id}
        )
        return self.client.get(url, *args, **kwargs)

    def _postas(self, group_id, invite_id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
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
        self.assertEquals(selector.one('.page-header h1').alltext_normalized, 'Delete group invite')
        self.assertEquals(selector.one('.page-header p').alltext_normalized, 'assignment1 - duck1010 - active')

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
