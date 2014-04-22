from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder


class TestGroupInviteOverviewView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _getas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_groupinvite_overview', kwargs={'group_id': id})
        return self.client.get(url, *args, **kwargs)

    def _postas(self, id, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_groupinvite_overview', kwargs={'group_id': id})
        return self.client.post(url, *args, **kwargs)
