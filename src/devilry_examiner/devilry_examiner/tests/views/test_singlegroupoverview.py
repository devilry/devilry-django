from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet


class TestSingleGroupOverview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1').user
        self.week1builder = NodeBuilder('ducku')\
                .add_subject('duck1010')\
                .add_6month_active_period('current')\
                .add_assignment('week1')

    def _getas(self, username, groupid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupid}),
                *args, **kwargs)

    def test_header(self):
        groupbuilder = self.week1builder.add_group(students=[self.student1], examiners=[self.examiner1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        print html
        #pageheader = cssGet(html, '.assignmentheader h1').strip()
        #self.assertEquals(len(listitems), 1)
        #self.assertEquals(listitems[0].text.strip(), 'sub.period1.week2')
