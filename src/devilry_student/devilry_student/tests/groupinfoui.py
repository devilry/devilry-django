#from devilry.apps.core.models import 
from devilry.apps.core.testhelper import TestHelper

from .base import StudentSeleniumTestCase


class TestGroupInfoUI(StudentSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()

    def _browseToGroup(self, groupid):
        self.browseTo('/group/{groupid}/'.format(groupid=groupid))

    def _browseToDelivery(self, groupid, deliveryid):
        self.browseTo('/group/{groupid}/{deliveryid}'.format(groupid=groupid,
                                                             deliveryid=deliveryid))

    def test_doesnotexists(self):
        self.testhelper.create_user('student1')
        self.login('student1')
        self._browseToGroup(100000)
        self.waitForCssSelector('.devilry_extjsextras_alertmessage')
        self.assertTrue('Permission denied' in self.selenium.page_source)
