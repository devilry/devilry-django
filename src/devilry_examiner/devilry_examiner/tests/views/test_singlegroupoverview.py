from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet


class TestSingleGroupOverview(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _getas(self, username, groupid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupid}),
                *args, **kwargs)

    def test_header(self):
        self.testhelper.add(nodes='uni',
                subjects=['sub'],
                periods=['period1:begins(-2)'], # 2 months ago
                assignments=['week2:pub(1)'], # 2 months + 1day ago
                assignmentgroups=['g1:candidate(student1):examiner(examiner1)'])
        response = self._getas('examiner1', self.testhelper.sub_period1_week2_g1.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        #pageheader = cssGet(html, '.assignmentheader h1').strip()
        #self.assertEquals(len(listitems), 1)
        #self.assertEquals(listitems[0].text.strip(), 'sub.period1.week2')
