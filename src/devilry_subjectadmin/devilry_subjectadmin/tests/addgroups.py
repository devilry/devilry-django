from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


class TestAddGroups(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub:admin(subadmin)'],
                            periods=['p1:admin(p1admin)'],
                            assignments=['a1:admin(a1admin)'])
        self.period = self.testhelper.sub_p1

    def _loginTo(self, username, assignmentid):
        self.loginTo(username, '/assignment/{id}/@@manage-students/@@add-students'.format(id=assignmentid))

    def _add_relatedstudent(self, username, full_name=None, tags='', candidate_id=None):
        user = self.testhelper.create_user(username, fullname=full_name)
        self.period.relatedstudent_set.create(user=user,
                                              tags=tags,
                                              candidate_id=candidate_id)

    def test_render(self):
        self._add_relatedstudent('student1', 'Student One')
        self._add_relatedstudent('student2', 'Student Two')

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        #raw_input('p')
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.devilry_subjectadmin_addgroupspanel')
        self.waitForText('Choose the students you want to add')
        self.waitForText('Missing students?')
        self.waitForText('Only students registered on')
        link = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_addstudentsoverview a.addoreditstudents_link')
        self.assertEquals(link.text, 'Add or edit students on sub.p1')
