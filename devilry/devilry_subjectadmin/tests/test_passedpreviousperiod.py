import json

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import deliverytypes
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase


class TestPassedPreviousPeriod(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_user('student1', 'Student One')
        self.testhelper.add(
            nodes='uni',
            subjects=['sub:admin(subadmin)'],
            periods=['p1:begins(-14):ends(6)',
                     'p2:begins(-2):ends(6)'],
            assignments=['a1:pub(1)'],
            assignmentgroups=[
                'g1:candidate(student1):examiner(examiner1)'
            ],
            deadlines=['d1:ends(10)']
        )
        self.assignment = self.testhelper.sub_p1_a1

    def _loginTo(self, username, assignmentid):
        self.loginTo(username, '/assignment/{id}/@@passed-previous-period'.format(id=assignmentid))

    def _find_gridrows(self, grid):
        return grid.find_elements_by_css_selector('.x-grid-row')

    def _get_row_by_group(self, grid, group):
        cssselector = '.groupinfo_{id}'.format(id=group.id)
        self.waitFor(grid, lambda g: len(grid.find_elements_by_css_selector(cssselector)) == 1)
        for row in self._find_gridrows(grid):
            matches = row.find_elements_by_css_selector(cssselector)
            if len(matches) > 0:
                return row
        raise ValueError('Could not find any rows matching the following group: {0}.'.format(group))

    def _click_group_selector(self, grid, group):
        self._get_row_by_group(grid, group).find_element_by_css_selector('.x-grid-row-checker').click()

    def _get_selectgroupsgrid(self):
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_selectpassedpreviousgroupssgrid')

    def _get_editgradegrid(self):
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_editpassedpreviousgroupssgrid')

    def _set_grade_for_group(self, group, value):
        grid = self._get_editgradegrid()
        row = self._get_row_by_group(grid, group)
        tds = row.find_elements_by_css_selector('td')
        tds[1].click()
        editorselector = '.x-grid-editor input[type=text]'
        inputfield = self.waitForAndFindElementByCssSelector(editorselector)
        inputfield.clear()
        inputfield.send_keys(value)
        grid.click()
        self.waitForNotDisplayed(inputfield)

    def _wait_for_rowcount(self, grid, rowcount):
        self.waitFor(grid, lambda g: len(self._find_gridrows(g)) == rowcount)

    def _click_show_hidden_groups_checkbox(self):
        button = self.waitForAndFindElementByCssSelector(
            '.devilry_subjectadmin_passedpreviousperiodoverview .showUnRecommendedCheckbox input[type=button]')
        button.click()

    def test_render(self):
        self.testhelper.create_feedbacks(
            (self.testhelper.sub_p1_a1_g1, {'grade': 'B', 'points': 86, 'is_passing_grade': True})
        )
        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)

        p2_a1_g1 = self.testhelper.sub_p2_a1_g1
        grid = self._get_selectgroupsgrid()
        self.assertEquals(len(self._find_gridrows(grid)), 1)
        row = self._get_row_by_group(grid, p2_a1_g1)
        self.assertEqual(row.find_element_by_css_selector('.groupinfo .names').text.strip(), 'Student One')
        self.assertEqual(row.find_element_by_css_selector('.groupinfo .usernames').text.strip(), 'student1')

    def _test_whyignored(self, group, whyignored_class, whyignored_text):
        grid = self._get_selectgroupsgrid()
        self.assertEquals(len(self._find_gridrows(grid)), 0)
        self._click_show_hidden_groups_checkbox()
        self._wait_for_rowcount(grid, 1)
        row = self._get_row_by_group(grid, group)
        self.assertEqual(row.find_element_by_css_selector('.groupinfo .names').text.strip(), 'Student One')
        cssselector = '.oldgroup_or_ignoredinfo .whyignored_{0}'.format(whyignored_class)
        self.assertEqual(1, len(row.find_elements_by_css_selector(cssselector)))
        self.assertEqual(
            row.find_element_by_css_selector('.oldgroup_or_ignoredinfo .whyignored').text.strip(),
            whyignored_text)

    def test_ignored_only_failing_grade_in_previous(self):
        self.testhelper.create_feedbacks(
            (self.testhelper.sub_p1_a1_g1, {'grade': 'F', 'points': 0, 'is_passing_grade': False})
        )
        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        self._test_whyignored(
            self.testhelper.sub_p2_a1_g1,
            'only_failing_grade_in_previous',
            'The student has delivered this assignment previously, but never achieved a passing grade.')

    def test_ignored_has_alias_feedback(self):
        # Add an alias delivery to the P2 assignment
        delivery = self.testhelper.add_delivery(self.testhelper.sub_p2_a1_g1)
        delivery.delivery_type = deliverytypes.ALIAS
        delivery.save()
        self.testhelper.add_feedback(delivery, verdict={'grade': 'B', 'points': 86, 'is_passing_grade': True})

        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        self._test_whyignored(
            self.testhelper.sub_p2_a1_g1,
            'has_alias_feedback',
            'Is already marked as previously passed.')

    def test_ignored_has_feedback(self):
        self.testhelper.create_feedbacks(
            (self.testhelper.sub_p2_a1_g1, {'grade': 'A', 'points': 70, 'is_passing_grade': True})
        )
        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        self._test_whyignored(
            self.testhelper.sub_p2_a1_g1,
            'has_feedback',
            'Group has feedback for this assignment.')

    def test_allignoredmessage(self):
        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        warning = self.waitForAndFindElementByCssSelector(
            '.devilry_extjsextras_floatingalertmessagelist .no-nonignoredgroups-warning')
        self.assertIn(
            'We did not detect any groups that Devilry does not believe should '
            'be ignored. Use the checkbox below the table to see and select ignored groups.',
            warning.text)

    def _click_nextbutton(self):
        button = self.waitForAndFindElementByCssSelector(
            '.devilry_subjectadmin_passedpreviousperiodoverview .nextButton button')
        self.waitForEnabled(button)
        button.click()

    def _click_savebutton(self):
        button = self.waitForAndFindElementByCssSelector(
            '.devilry_subjectadmin_passedpreviousperiodoverview .saveButton button')
        self.waitForEnabled(button)
        button.click()

    def _set_grade_editor(self, assignment, gradeeditorid, config):
        assignment.gradeeditor_config.gradeeditorid = gradeeditorid
        assignment.gradeeditor_config.config = config
        assignment.gradeeditor_config.save()

    def _test_save_autodetected(self, gradeeditor, config=None):
        self._set_grade_editor(self.testhelper.sub_p2_a1, gradeeditor, config)
        self.assertEquals(self.testhelper.sub_p2_a1_g1_d1.deliveries.count(), 0)
        self.testhelper.create_feedbacks(
            (self.testhelper.sub_p1_a1_g1, {'grade': 'B', 'points': 86, 'is_passing_grade': True})
        )
        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        self._click_nextbutton()
        self._click_savebutton()
        successmessage = self.waitForAndFindElementByCssSelector(
            '.devilry_extjsextras_floatingalertmessagelist .passed-previously-sync-success')
        self.assertIn('Marked 1 groups as previously passed.', successmessage.text)
        self.assertEquals(self.testhelper.sub_p2_a1_g1_d1.deliveries.count(), 1)

    def test_save_approved_autodetected(self):
        self._test_save_autodetected('approved')

    def _test_save_manual(self, gradeeditor, config=None, value=None):
        self._set_grade_editor(self.testhelper.sub_p2_a1, gradeeditor, config)
        self.assertEquals(self.testhelper.sub_p2_a1_g1_d1.deliveries.count(), 0)

        self._loginTo('subadmin', self.testhelper.sub_p2_a1.id)
        self._click_show_hidden_groups_checkbox()
        group = self.testhelper.sub_p2_a1_g1
        self._click_group_selector(self._get_selectgroupsgrid(), group)
        self._click_nextbutton()

        if value:
            self._set_grade_for_group(group, value)
        self._click_savebutton()
        successmessage = self.waitForAndFindElementByCssSelector(
            '.devilry_extjsextras_floatingalertmessagelist .passed-previously-sync-success')
        self.assertIn('Marked 1 groups as previously passed.', successmessage.text)
        self.assertEquals(self.testhelper.sub_p2_a1_g1_d1.deliveries.count(), 1)

    def test_save_approved_manual(self):
        self._test_save_manual('approved')
