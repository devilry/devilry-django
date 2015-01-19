from datetime import datetime, timedelta
from time import sleep

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase


class TestDeadlines(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2)'],
                            assignments=['a1:admin(a1admin):pub(1)'])
        self.assignment = self.testhelper.sub_p1_a1

    def _loginTo(self, username, assignmentid):
        self.loginTo(username, '/assignment/{id}/@@bulk-manage-deadlines/'.format(id=assignmentid))

    def _find_gridrows(self, grid):
        return grid.find_elements_by_css_selector('.x-grid-row')

    def _get_row_by_group(self, grid, group):
        cssselector = '.groupInfoWrapper_{id}'.format(id=group.id)
        self.waitFor(grid, lambda g: len(grid.find_elements_by_css_selector(cssselector)) == 1)
        for row in self._find_gridrows(grid):
            matches = row.find_elements_by_css_selector(cssselector)
            if len(matches) > 0:
                return row
        raise ValueError('Could not find any rows matching the following group: {0}.'.format(group))

    def _click_row_by_group(self, grid, group):
        self._get_row_by_group(grid, group).find_element_by_css_selector('.x-grid-row-checker').click()

    def _get_addbutton(self):
        return self.waitForAndFindElementByCssSelector('.add_deadline_button')

    def _open_addform(self):
        self._get_addbutton().click()
        return self.waitForAndFindElementByCssSelector(
            '.devilry_subjectadmin_bulkmanagedeadlines_deadlineform.createdeadlineform')

    def _create_datestring_from_offset(self, dayoffset=1):
        now = datetime.now()
        datetimeObj = now + timedelta(days=1)
        datestring = datetimeObj.date().isoformat()
        return datestring

    def _create_badgroup(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.badgroup:candidate(student1):examiner(examiner1).d1')
        badgroup = self.testhelper.sub_p1_a1_badgroup
        self.testhelper.add_delivery(badgroup, {'f.py': ['print ', 'meh']})
        self.testhelper.add_feedback(badgroup, verdict={'grade': 'F', 'points': 1, 'is_passing_grade': False})
        return badgroup

    def _create_goodgroup(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.goodgroup:candidate(student1):examiner(examiner1).d1')
        goodgroup = self.testhelper.sub_p1_a1_goodgroup
        self.testhelper.add_delivery(goodgroup, {'a.py': ['print ', 'yess']})
        self.testhelper.add_feedback(goodgroup, verdict={'grade': 'A', 'points': 100, 'is_passing_grade': True})
        return goodgroup

    def _create_nodeadlinegroup(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.nodeadlinegroup:candidate(student1):examiner(examiner1)')
        return self.testhelper.sub_p1_a1_nodeadlinegroup

    def _create_nofeedbackgroup(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.nofeedbackgroup:candidate(student1):examiner(examiner1).d1')
        nofeedbackgroup = self.testhelper.sub_p1_a1_nofeedbackgroup
        self.testhelper.add_delivery(nofeedbackgroup, {'a.py': ['print ', 'yess']})
        return nofeedbackgroup

    def _get_formsavebutton(self, form):
        return form.find_element_by_css_selector('.savedeadlinebutton button')

    #
    #
    # Add deadline tests
    #
    #
    def _fill_addform(self, form, date, time, text='', createmodecls=None):
        datefield = self.waitForAndFindElementByCssSelector(
            '.deadlinefield .devilry_extjsextras_datefield input[type=text]',
            within=form)
        timefield = self.waitForAndFindElementByCssSelector(
            '.deadlinefield .devilry_extjsextras_timefield input[type=text]',
            within=form)
        textfield = self.waitForAndFindElementByCssSelector('textarea[name="text"]', within=form)

        for field in (datefield, timefield, textfield):
            field.clear()
        datefield.clear()
        datefield.send_keys('')
        datefield.send_keys(date)

        timefield.clear()
        timefield.send_keys('')
        timefield.send_keys(time)

        textfield.clear()
        textfield.send_keys('')
        textfield.send_keys(text)

        if createmodecls:
            checkbox = form.find_element_by_css_selector('.{0} input[type=button]'.format(createmodecls))
            checkbox.click()

    def test_add_deadline_failed(self):
        nodeadlinegroup = self._create_nodeadlinegroup()
        nofeedbackgroup = self._create_nofeedbackgroup()
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()
        self.assertEquals(len(nodeadlinegroup.deadlines.all()), 0)
        self.assertEquals(len(nofeedbackgroup.deadlines.all()), 1)
        self.assertEquals(len(badgroup.deadlines.all()), 1)
        self.assertEquals(len(goodgroup.deadlines.all()), 1)

        self._loginTo('a1admin', self.assignment.id)
        addform = self._open_addform()
        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                           time='12:00', text='Hello', createmodecls='createmode_failed')

        url = self.selenium.current_url
        self._get_formsavebutton(addform).click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        nofeedbackgroup = self.testhelper.reload_from_db(nofeedbackgroup)
        badgroup = self.testhelper.reload_from_db(badgroup)
        goodgroup = self.testhelper.reload_from_db(goodgroup)

        # Has new deadline:
        self.assertEquals(len(badgroup.deadlines.all()), 2)

        # Unchaged:
        self.assertEquals(len(nodeadlinegroup.deadlines.all()), 0)
        self.assertEquals(len(nofeedbackgroup.deadlines.all()), 1)
        self.assertEquals(len(goodgroup.deadlines.all()), 1)

        newdeadline = badgroup.deadlines.all()[0]
        self.assertEquals(newdeadline.text, 'Hello')
        self.assertEquals(newdeadline.deadline.hour, 12)
        self.assertEquals(newdeadline.deadline.minute, 0)

    def test_add_deadline_failed_or_no_feedback(self):
        nodeadlinegroup = self._create_nodeadlinegroup()
        nofeedbackgroup = self._create_nofeedbackgroup()
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()

        self._loginTo('a1admin', self.assignment.id)
        addform = self._open_addform()
        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                        time='12:00', text='Hello', createmodecls='createmode_failed_or_no_feedback')

        url = self.selenium.current_url
        self._get_formsavebutton(addform).click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        nofeedbackgroup = self.testhelper.reload_from_db(nofeedbackgroup)
        badgroup = self.testhelper.reload_from_db(badgroup)
        goodgroup = self.testhelper.reload_from_db(goodgroup)

        # Has new deadline:
        self.assertEquals(len(nodeadlinegroup.deadlines.all()), 1)
        self.assertEquals(len(nofeedbackgroup.deadlines.all()), 2)
        self.assertEquals(len(badgroup.deadlines.all()), 2)

        # Unchaged:
        self.assertEquals(len(goodgroup.deadlines.all()), 1)

    def test_add_deadline_no_deadlines(self):
        nodeadlinegroup = self._create_nodeadlinegroup()
        nofeedbackgroup = self._create_nofeedbackgroup()
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()

        self._loginTo('a1admin', self.assignment.id)
        addform = self._open_addform()
        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                           time='12:00', text='Hello', createmodecls='createmode_no_deadlines')

        url = self.selenium.current_url
        self._get_formsavebutton(addform).click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        nofeedbackgroup = self.testhelper.reload_from_db(nofeedbackgroup)
        badgroup = self.testhelper.reload_from_db(badgroup)
        goodgroup = self.testhelper.reload_from_db(goodgroup)

        # Has new deadline:
        self.assertEquals(len(nodeadlinegroup.deadlines.all()), 1)

        # Unchanged:
        self.assertEquals(len(nofeedbackgroup.deadlines.all()), 1)
        self.assertEquals(len(badgroup.deadlines.all()), 1)
        self.assertEquals(len(goodgroup.deadlines.all()), 1)

    def _click_specific_groups(self, addform, groups):
        grid = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_bulkmanagedeadlines_allgroupsgrid',
                                                       within=addform)
        for group in groups:
            self._click_row_by_group(grid, group)

    def test_add_deadline_specific_groups(self):
        nodeadlinegroup = self._create_nodeadlinegroup()
        nofeedbackgroup = self._create_nofeedbackgroup()
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()

        self._loginTo('a1admin', self.assignment.id)
        addform = self._open_addform()
        savebutton = self._get_formsavebutton(addform)
        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                        time='12:00', text='Hello', createmodecls='createmode_specific_groups')
        self.waitForDisabled(savebutton)
        self._click_specific_groups(addform, [goodgroup, badgroup])
        self.waitForEnabled(savebutton)

        url = self.selenium.current_url
        savebutton.click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        nofeedbackgroup = self.testhelper.reload_from_db(nofeedbackgroup)
        badgroup = self.testhelper.reload_from_db(badgroup)
        goodgroup = self.testhelper.reload_from_db(goodgroup)

        # Has new deadline:
        self.assertEquals(len(badgroup.deadlines.all()), 2)
        self.assertEquals(len(goodgroup.deadlines.all()), 2)

        # Unchanged:
        self.assertEquals(len(nofeedbackgroup.deadlines.all()), 1)
        self.assertEquals(len(nodeadlinegroup.deadlines.all()), 0)

    def test_add_deadline_enable_disable(self):
        goodgroup = self._create_goodgroup()
        self._loginTo('a1admin', self.assignment.id)

        addform = self._open_addform()
        savebutton = self._get_formsavebutton(addform)

        self.waitForDisabled(savebutton)  # Should start as disabled

        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                           time='12:00', text='Hello')
        self.waitForEnabled(savebutton)

        self._fill_addform(addform, date='',
                           time='12:00', text='Hello')
        self.waitForDisabled(savebutton)

        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                           time='12:00', text='Hello', createmodecls='createmode_specific_groups')
        self.waitForDisabled(savebutton)

        self._click_specific_groups(addform, [goodgroup]) # Select goodgroup
        self.waitForEnabled(savebutton)

        self._click_specific_groups(addform, [goodgroup]) # Deselect goodgroup
        self.waitForDisabled(savebutton)

        self._fill_addform(addform, date=self._create_datestring_from_offset(2),
                           time='12:00', text='Hello', createmodecls='createmode_failed')
        self.waitForEnabled(savebutton)

    #
    #
    # Edit deadline tests
    #
    #
    def _fill_editform(self, form, date, time, text=''):
        self._fill_addform(form, date, time, text)

    def _get_deadlinepanels(self, expectedcount):
        cssselector = '.devilry_subjectadmin_bulkmanagedeadlines_deadline'
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector(cssselector)) == expectedcount)
        return self.selenium.find_elements_by_css_selector(cssselector)

    def _expand_deadlinepanel(self, deadlinepanel):
        button = deadlinepanel.find_element_by_css_selector('.x-panel-header .x-tool-expand-bottom')
        button.click()
        return self.waitForAndFindElementByCssSelector('.bulkmanagedeadlines_deadline_body', within=deadlinepanel)

    def _expand_deadline_by_index(self, index, expectedcount):
        return self._expand_deadlinepanel(self._get_deadlinepanels(expectedcount)[index])

    def _open_editform(self, deadlinepanelbody):
        button = self.waitForAndFindElementByCssSelector('.edit_deadline_button', within=deadlinepanelbody)
        button.click()
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_bulkmanagedeadlines_deadlineform.editdeadlineform',
                                                       within=deadlinepanelbody)

    def _click_onlysomegroups_checkbox(self, editform):
        checkbutton = editform.find_element_by_css_selector('.edit_specific_groups_fieldset .x-fieldset-header-checkbox input.x-form-checkbox')
        checkbutton.click()

    def _editform_clickgroups(self, editform, groups):
        grid = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_bulkmanagedeadlines_groupsindeadlineselectgrid',
                                                       within=editform)
        for group in groups:
            self._click_row_by_group(grid, group)


    def test_edit_deadline(self):
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()
        self._loginTo('a1admin', self.assignment.id)
        deadlinepanelbody = self._expand_deadline_by_index(index=0, expectedcount=1)
        editform = self._open_editform(deadlinepanelbody)
        self._fill_editform(editform, date=self._create_datestring_from_offset(2),
                            time='12:00', text='Hello')

        url = self.selenium.current_url
        self._get_formsavebutton(editform).click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        for group in badgroup, goodgroup:
            deadline = group.deadlines.all()[0]
            self.assertEquals(deadline.text, 'Hello')
            self.assertEquals(deadline.deadline.hour, 12)
            self.assertEquals(deadline.deadline.minute, 0)

    def test_edit_deadline_afterperiod(self):
        goodgroup = self._create_goodgroup()
        self._loginTo('a1admin', self.assignment.id)

        deadlinepanelbody = self._expand_deadline_by_index(index=0, expectedcount=1)
        editform = self._open_editform(deadlinepanelbody)
        alertmessagelist = editform.find_element_by_css_selector('.devilry_extjsextras_alertmessagelist')
        self.assertEquals(alertmessagelist.find_elements_by_css_selector('.alert-error'), [])

        year = goodgroup.deadlines.all()[0].deadline.year
        self._fill_editform(editform, date='{0}-01-01'.format(year+3), time='12:00')
        self._get_formsavebutton(editform).click()

        def has_out_of_period_error(a):
            if len(alertmessagelist.find_elements_by_css_selector('.alert-error')) == 1:
                error = alertmessagelist.find_element_by_css_selector('.alert-error')
                return 'Deadline must be within' in error.text
            return False
        self.waitFor(alertmessagelist, has_out_of_period_error)

    def test_edit_deadline_beforepubtime(self):
        goodgroup = self._create_goodgroup()
        self._loginTo('a1admin', self.assignment.id)

        deadlinepanelbody = self._expand_deadline_by_index(index=0, expectedcount=1)
        editform = self._open_editform(deadlinepanelbody)
        alertmessagelist = editform.find_element_by_css_selector('.devilry_extjsextras_alertmessagelist')
        self.assertEquals(alertmessagelist.find_elements_by_css_selector('.alert-error'), [])

        self._fill_editform(editform, date='2000-01-01', time='12:00')
        self._get_formsavebutton(editform).click()

        def has_out_of_period_error(a):
            if len(alertmessagelist.find_elements_by_css_selector('.alert-error')) == 1:
                error = alertmessagelist.find_element_by_css_selector('.alert-error')
                return 'Deadline cannot be before publishing time' in error.text
            return False
        self.waitFor(alertmessagelist, has_out_of_period_error)

    def test_edit_deadline_somegroups(self):
        badgroup = self._create_badgroup()
        goodgroup = self._create_goodgroup()
        goodgroup_deadline = goodgroup.deadlines.all()[0].deadline
        self._loginTo('a1admin', self.assignment.id)

        deadlinepanelbody = self._expand_deadline_by_index(index=0, expectedcount=1)
        editform = self._open_editform(deadlinepanelbody)
        self._fill_editform(editform, date=self._create_datestring_from_offset(2),
                            time='12:00', text='Hello')
        self._click_onlysomegroups_checkbox(editform)
        sleep(1)
        self._editform_clickgroups(editform, [badgroup])

        url = self.selenium.current_url
        self._get_formsavebutton(editform).click()
        self.waitFor(self.selenium, lambda s: s.current_url != url) # Wait for the page to be reloaded with the new deadline URL

        # Goodgroup is unchanged?
        self.assertEquals(goodgroup.deadlines.all()[0].deadline, goodgroup_deadline)

        # Badgroup was updated?
        deadline = badgroup.deadlines.all()[0]
        self.assertEquals(deadline.text, 'Hello')
        self.assertEquals(deadline.deadline.hour, 12)
        self.assertEquals(deadline.deadline.minute, 0)

    def test_edit_deadline_enable_disable(self):
        badgroup = self._create_badgroup()
        self._create_goodgroup()
        self._loginTo('a1admin', self.assignment.id)

        deadlinepanelbody = self._expand_deadline_by_index(index=0, expectedcount=1)
        editform = self._open_editform(deadlinepanelbody)
        savebutton = self._get_formsavebutton(editform)

        self.waitForEnabled(savebutton)  # Should start as enabled since we load a valid deadline

        self._fill_editform(editform, date='',
                            time='12:00', text='Hello')
        self.waitForDisabled(savebutton)

        self._fill_editform(editform, date=self._create_datestring_from_offset(2),
                            time='12:00', text='Hello')
        self.waitForEnabled(savebutton)

        self._click_onlysomegroups_checkbox(editform)  # Expand only some groups panel
        self.waitForDisabled(savebutton)

        self._editform_clickgroups(editform, [badgroup])  # Select badgroup
        self.waitForEnabled(savebutton)

        self._editform_clickgroups(editform, [badgroup])  # Deselect badgroup
        self.waitForDisabled(savebutton, timeout=10)

        self._click_onlysomegroups_checkbox(editform)  # Collapse only some groups panel
        self.waitForEnabled(savebutton)
