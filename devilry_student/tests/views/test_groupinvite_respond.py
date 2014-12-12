from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder


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
        html = response.content
        self.assertEquals(cssGet(html, 'h1').text.strip(), 'Respond to group inviteduck1010.active.assignment1')

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