from django.test import TestCase
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.apps.core.models import GroupInvite
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
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
