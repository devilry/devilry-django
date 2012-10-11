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
        self.assignment = self.testhelper.sub_p1_a1

    def _loginTo(self, username, assignmentid):
        self.loginTo(username, '/assignment/{id}/@@manage-students/@@add-students'.format(id=assignmentid))

    def _add_relatedstudent(self, username, full_name=None, tags='', candidate_id=None):
        user = self.testhelper.create_user(username, fullname=full_name)
        self.period.relatedstudent_set.create(user=user,
                                              tags=tags,
                                              candidate_id=candidate_id)

    def _add_relatedexaminer(self, username, full_name=None, tags=''):
        user = self.testhelper.create_user(username, fullname=full_name)
        self.period.relatedexaminer_set.create(user=user,
                                               tags=tags)

    def _find_gridrows(self):
        return self.selenium.find_elements_by_css_selector('.relatedstudentsgrid .x-grid-row')

    def _get_row_by_username(self, username):
        cssselector = '.relatedstudentsgrid .x-grid-row .userinfo_{username}'.format(username=username)
        self.waitForCssSelector(cssselector)
        for row in self._find_gridrows():
            matches = row.find_elements_by_css_selector(cssselector)
            if len(matches) > 0:
                return row
        raise ValueError('Could not find any rows matching the following username: {0}.'.format(username))

    def _click_row_by_username(self, username, add_to_selection=True):
        self._get_row_by_username(username).click()

    def _get_addbutton(self):
        return self.waitForAndFindElementByCssSelector('.addselectedbutton')

    def _get_includetagscheckbox(self):
        return self.waitForAndFindElementByCssSelector('.includetagscheckbox')

    def _get_autosetexaminerscheckbox(self):
        return self.waitForAndFindElementByCssSelector('.autosetexaminerscheckbox')

    def _expand_morehelp(self):
        self.waitForAndFindElementByCssSelector('.sidebarpanel .morebutton').click()
        self.waitForDisplayed('.sidebarpanel .lessbutton')

    def _is_checked(self, checkbox):
        return 'x-form-cb-checked' in checkbox.get_attribute('class').split()

    def _set_checkbox(self, checkbox, check):
        if self._is_checked(checkbox) and check:
            raise ValueError('Checkbox is already checked')
        if not self._is_checked(checkbox) and not check:
            raise ValueError('Checkbox is already unchecked')
        checkbox.find_element_by_css_selector('input[type=button]').click()

    def test_render_sidebar(self):
        self._add_relatedstudent('student1')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.sidebarpanel')
        self.waitForText('Choose the students you want to add')

    def test_render_morehelp(self):
        self._add_relatedstudent('student1')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self._expand_morehelp()
        self.waitForText('Missing students?')
        self.waitForText('Only students registered on')
        link = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_addstudentsoverview a.addoreditstudents_link')
        self.assertEquals(link.text, 'Add or edit students on sub.p1')

    def test_render_grid(self):
        self._add_relatedstudent('student1', 'Student One', tags='group1,group2')
        self._add_relatedstudent('student2', full_name=None)

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview .relatedstudentsgrid')

        student1row = self._get_row_by_username('student1')
        self.assertEquals(student1row.find_element_by_css_selector('.full_name').text.strip(), 'Student One')
        self.assertEquals(student1row.find_element_by_css_selector('.username').text.strip(), 'student1')

        student2row = self._get_row_by_username('student2')
        self.assertEquals(student2row.find_element_by_css_selector('.full_name').text.strip(), 'Full name missing')
        self.assertEquals(student2row.find_element_by_css_selector('.username').text.strip(), 'student2')

        tags = student1row.find_element_by_css_selector('.tags')
        tags_and_examiners = student1row.find_element_by_css_selector('.tags_and_examiners')

    def test_autosetexaminers(self):
        self._add_relatedstudent('student1', 'Student One', tags='group1,group2')
        self._add_relatedstudent('student2', full_name=None)
        self._add_relatedexaminer('examiner1', 'Examiner One', tags='group1')

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview .relatedstudentsgrid')

        student1row = self._get_row_by_username('student1')
        tags_and_examiners = student1row.find_element_by_css_selector('.tags_and_examiners')
        self._set_checkbox(self._get_autosetexaminerscheckbox(), check=True)
        self.assertEquals(len(tags_and_examiners.find_elements_by_css_selector('li')), 2)
        group1examiner = tags_and_examiners.find_element_by_css_selector('.tag_group1 .examiners').text.strip()
        self.assertEquals(group1examiner, 'Examiner One')
        group2examiner = tags_and_examiners.find_element_by_css_selector('.tag_group2 .examiners').text.strip()
        self.assertEquals(group2examiner, 'No matching examiners')


    def test_add_student(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1')
        self._add_relatedstudent('student2')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')

        includetagscheckbox = self._get_includetagscheckbox()
        self.assertTrue(self._is_checked(includetagscheckbox))
        autosetexaminerscheckbox = self._get_autosetexaminerscheckbox()
        self.assertFalse(self._is_checked(autosetexaminerscheckbox))

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview')
        groups = self.assignment.assignmentgroups.all()
        self.assertEquals(len(groups), 1)
        g1 = groups[0]
        self.assertEquals(g1.candidates.all()[0].student.username, 'student1')
