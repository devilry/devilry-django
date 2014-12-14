from datetime import datetime, timedelta

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase


class TestAddGroups(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub:admin(subadmin)'],
                            periods=['p1:admin(p1admin):begins(-2)'],
                            assignments=['a1:admin(a1admin):pub(1)'])
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
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.sidebarpanel .lessbutton')) == 1)

    def _is_checked(self, checkbox):
        return 'x-form-cb-checked' in checkbox.get_attribute('class').split()

    def _set_checkbox(self, checkbox, check):
        if self._is_checked(checkbox) and check:
            raise ValueError('Checkbox is already checked')
        if not self._is_checked(checkbox) and not check:
            raise ValueError('Checkbox is already unchecked')
        checkbox.find_element_by_css_selector('input[type=button]').click()

    def _set_first_deadline(self, date, time):
        datefield = self.waitForAndFindElementByCssSelector('.first_deadline_field .devilry_extjsextras_datefield input')
        timefield = self.waitForAndFindElementByCssSelector('.first_deadline_field .devilry_extjsextras_timefield input')
        datefield.clear()
        timefield.clear()
        datefield.send_keys(date)
        timefield.send_keys(time)

    def _set_valid_first_deadline(self):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        isoday_yesterday = yesterday.date().isoformat()
        self._set_first_deadline(isoday_yesterday, '12:00')
        return yesterday

    #
    #
    # Test rendering
    #
    #

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

    def test_render_autosetexaminers(self):
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


    #
    #
    # Add student(s)
    #
    #

    def test_add_student_include_tags(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1', tags='group1,group2')
        self._add_relatedstudent('student2')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')

        includetagscheckbox = self._get_includetagscheckbox()
        self.assertTrue(self._is_checked(includetagscheckbox))
        autosetexaminerscheckbox = self._get_autosetexaminerscheckbox()
        self.assertFalse(self._is_checked(autosetexaminerscheckbox))

        self._set_valid_first_deadline()
        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview')
        groups = self.assignment.assignmentgroups.all()
        self.assertEquals(len(groups), 1)

        g1 = groups[0]
        self.assertEquals(g1.candidates.all()[0].student.username, 'student1')
        self.assertEquals(g1.examiners.count(), 0)
        tags = [tag.tag for tag in g1.tags.all()]
        self.assertEquals(set(tags), set(['group1', 'group2']))

    def test_add_student_autosetexaminers(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1', 'Student One', tags='group1,group2')
        self._add_relatedstudent('student2', full_name=None)
        self._add_relatedexaminer('examiner1', 'Examiner One', tags='group1')
        self._add_relatedexaminer('examiner2', 'Examiner Two', tags='group1,other')

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview .relatedstudentsgrid')
        self._set_valid_first_deadline()
        self._set_checkbox(self._get_autosetexaminerscheckbox(), check=True)

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview')
        groups = self.assignment.assignmentgroups.all()
        self.assertEquals(len(groups), 1)

        g1 = groups[0]
        self.assertEquals(g1.candidates.all()[0].student.username, 'student1')
        examiners = g1.examiners.all()
        self.assertEquals(len(examiners), 2)
        examiner_usernames = [examiner.user.username for examiner in examiners]
        self.assertEquals(set(examiner_usernames), set(['examiner1', 'examiner2']))
        tags = [tag.tag for tag in g1.tags.all()]
        self.assertEquals(set(tags), set(['group1', 'group2']))

    def test_add_student_no_includetags(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1', 'Student One', tags='group1,group2')
        self._add_relatedstudent('student2', full_name=None)
        self._add_relatedexaminer('examiner1', 'Examiner One', tags='group1')
        self._add_relatedexaminer('examiner2', 'Examiner Two', tags='group1,other')

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview .relatedstudentsgrid')
        self._set_valid_first_deadline()
        self._set_checkbox(self._get_includetagscheckbox(), check=False)

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview')
        groups = self.assignment.assignmentgroups.all()
        self.assertEquals(len(groups), 1)

        g1 = groups[0]
        self.assertEquals(g1.candidates.all()[0].student.username, 'student1')
        self.assertEquals(g1.examiners.count(), 0)
        self.assertEquals(g1.tags.count(), 0)


    #
    #
    # All ignored variants
    #
    #

    def test_allignored(self):
        self._add_relatedstudent('student1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')

        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        panel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_addgroupsallignoredhelp')

        self.assertIn('No students available', panel.text)
        self.assertEquals(panel.find_element_by_css_selector('a.add_more_students_to_period_link').text.strip(),
                          'Add students to sub.p1')

    def test_allignored_no_relatedstudents(self):
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        panel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_addgroupsallignoredhelp')

        self.assertIn('No students available', panel.text)
        nostudents_warning = panel.find_element_by_css_selector('.no_students_on_period_warning')
        self.assertIn('There is no students on sub.p1', nostudents_warning.text)
        self.assertEquals(panel.find_element_by_css_selector('a.add_more_students_to_period_link').text.strip(),
                          'Add students to sub.p1')

    def test_allignored_not_periodadmin(self):
        self._add_relatedstudent('student1')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')

        self._loginTo('a1admin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        panel = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_addgroupsallignoredhelp')

        self.assertIn('No students available', panel.text)
        self.assertEquals(len(panel.find_elements_by_css_selector('a.add_more_students_to_period_link')), 0)
        not_periodadmin_warning = panel.find_element_by_css_selector('.not_periodadmin_warning')
        self.assertIn('You do not have administrator rights on sub.p1', not_periodadmin_warning.text)


    #
    #
    # First deadline (submission date)
    #
    #

    def test_first_deadline(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')
        yesterday = self._set_valid_first_deadline()

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsoverview')
        groups = self.assignment.assignmentgroups.all()
        self.assertEquals(len(groups), 1)

        g1 = groups[0]
        self.assertEquals(g1.candidates.all()[0].student.username, 'student1')
        deadlines = g1.deadlines.all()
        self.assertEquals(len(deadlines), 1)
        self.assertEquals(deadlines[0].deadline,
                          datetime(yesterday.date().year, yesterday.date().month, yesterday.date().day, 12, 0))

    def test_first_deadline_before_pubtime(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')

        self._set_first_deadline('2000-01-01', '12:00') # This is before the pubtime, and before the period starts, so it should raise an error

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForText('Submission date can not be before the publishing time')

    def test_first_deadline_after_period(self):
        self.assertEquals(len(self.assignment.assignmentgroups.all()), 0)
        self._add_relatedstudent('student1')
        self._loginTo('subadmin', self.testhelper.sub_p1_a1.id)
        self.waitForCssSelector('.devilry_subjectadmin_addstudentsoverview')

        deadlinedate = self.period.end_time + timedelta(days=10)
        isoday_deadlinedate = deadlinedate.date().isoformat()
        self._set_first_deadline(isoday_deadlinedate, '12:00')

        self._click_row_by_username('student1')
        self._get_addbutton().click()
        self.waitForText("Submission date must be within it's period")
