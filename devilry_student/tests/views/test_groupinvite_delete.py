from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder


class TestGroupInviteDeleteView(TestCase):
    def setUp(self):
        self.testfromuser = UserBuilder('testfromuser').user
        self.testtouser = UserBuilder('testtouser').user

    def _getas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_groupinvite_delete', kwargs={'invite_id': id})
        return self.client.get(url, *args, **kwargs)

    def _postas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_groupinvite_delete', kwargs={'invite_id': id})
        return self.client.post(url, *args, **kwargs)

    def test_render(self):
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(invite.id, self.testfromuser)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, 'h1').text.strip(), 'Delete group inviteduck1010.active.assignment1')

    def test_get_only_if_sender(self):
        notalloweduser = UserBuilder('notalloweduser').user
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._getas(invite.id, notalloweduser)
        self.assertEquals(response.status_code, 404)

    def test_post_only_if_sender(self):
        notalloweduser = UserBuilder('notalloweduser').user
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._postas(invite.id, notalloweduser)
        self.assertEquals(response.status_code, 404)
        self.assertTrue(GroupInvite.objects.filter(id=invite.id).exists())

    def test_post_ok(self):
        notalloweduser = UserBuilder('notalloweduser').user
        group = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_group(students=[self.testfromuser, notalloweduser]).group
        invite = group.groupinvite_set.create(
            sent_by=self.testfromuser,
            sent_to=self.testtouser)
        response = self._postas(invite.id, self.testfromuser)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(GroupInvite.objects.filter(id=invite.id).exists())