from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



class TestRelatedStudentsUI(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)'])
        self.period = self.testhelper.sub_p1

    def _browseToManageStudentsAs(self, username, period_id):
        path = '/period/{0}/@@related-students'.format(period_id)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_relatedstudents')

    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_relatedstudents {0}'.format(cssselector))
    def find_elements(self, cssselector):
        return self.selenium.find_elements_by_css_selector('.devilry_subjectadmin_relatedstudents {0}'.format(cssselector))

    def test_render(self):
        self._browseToManageStudentsAs('p1admin', self.period.id)
        self.waitForCssSelector('.devilry_subjectadmin_selectrelateduserpanel')

    def test_invalid_period_id(self):
        self._browseToManageStudentsAs('p1admin', 1000000)
        # Should get one error for Period, and one for relatedusers
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.devilry_extjsextras_alertmessage')) == 2)
        for message in self.find_elements('.devilry_extjsextras_alertmessage'):
            self.assertIn('403', message.text.strip())
