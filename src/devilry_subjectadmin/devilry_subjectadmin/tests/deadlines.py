from datetime import datetime, timedelta
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase


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

    #def _find_gridrows(self):
        #return self.selenium.find_elements_by_css_selector('.relatedstudentsgrid .x-grid-row')

    #def _get_row_by_username(self, username):
        #cssselector = '.relatedstudentsgrid .x-grid-row .userinfo_{username}'.format(username=username)
        #self.waitForCssSelector(cssselector)
        #for row in self._find_gridrows():
            #matches = row.find_elements_by_css_selector(cssselector)
            #if len(matches) > 0:
                #return row
        #raise ValueError('Could not find any rows matching the following username: {0}.'.format(username))

    #def _click_row_by_username(self, username):
        #self._get_row_by_username(username).click()

    def _get_addbutton(self):
        return self.waitForAndFindElementByCssSelector('.add_deadline_button')

    def _open_addform(self):
        self._get_addbutton().click()
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_bulkmanagedeadlines_deadlineform')

    def _fill_form(self, form, date, time, text='', createmodecls=None):
        datefield = form.find_element_by_css_selector('.deadlinefield .devilry_extjsextras_datefield input[type=text]')
        timefield = form.find_element_by_css_selector('.deadlinefield .devilry_extjsextras_timefield input[type=text]')
        textfield = form.find_element_by_css_selector('textarea[name="text"]')

        for field in (datefield, timefield, textfield):
            field.clear()
        datefield.send_keys(date)
        timefield.send_keys(time)
        textfield.send_keys(text)
        if createmodecls:
            checkbox = form.find_element_by_css_selector('.{0} input[type=button]'.format(createmodecls))
            checkbox.click()

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
        self._fill_form(addform, date=self._create_datestring_from_offset(2),
                        time='12:00', text='Hello', createmodecls='createmode_failed')

        url = self.selenium.current_url
        addform.find_element_by_css_selector('.savedeadlinebutton').click()
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
        self._fill_form(addform, date=self._create_datestring_from_offset(2),
                        time='12:00', text='Hello', createmodecls='createmode_failed_or_no_feedback')

        url = self.selenium.current_url
        addform.find_element_by_css_selector('.savedeadlinebutton').click()
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
        self._fill_form(addform, date=self._create_datestring_from_offset(2),
                        time='12:00', text='Hello', createmodecls='createmode_no_deadlines')

        url = self.selenium.current_url
        addform.find_element_by_css_selector('.savedeadlinebutton').click()
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
