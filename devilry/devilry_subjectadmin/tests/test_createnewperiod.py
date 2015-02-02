from datetime import datetime

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase


class TestCreateNewPeriod(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub:admin(subadmin)'])

    def _loginTo(self, username, id):
        self.loginTo(username, '/subject/{id}/@@create-new-period'.format(id=id))

    def _waitForFields(self):
        self.short_name_field = self.waitForAndFindElementByCssSelector('input[name=short_name]')
        self.long_name_field = self.waitForAndFindElementByCssSelector('input[name=long_name]')
        self.start_time_datefield = self.waitForAndFindElementByCssSelector('.start_time_field .devilry_extjsextras_datefield input')
        self.start_time_timefield = self.waitForAndFindElementByCssSelector('.start_time_field .devilry_extjsextras_timefield input')
        self.end_time_datefield = self.waitForAndFindElementByCssSelector('.end_time_field .devilry_extjsextras_datefield input')
        self.end_time_timefield = self.waitForAndFindElementByCssSelector('.end_time_field .devilry_extjsextras_timefield input')
        self.savebutton = self.waitForAndFindElementByCssSelector('.devilry_primarybutton button')

    def _set_values(self,
                    short_name,
                    long_name,
                    start_date, start_time,
                    end_date, end_time):
        self.long_name_field.clear()
        self.start_time_datefield.clear()
        self.start_time_timefield.clear()
        self.end_time_datefield.clear()
        self.end_time_timefield.clear()

        self.long_name_field.send_keys('')
        self.long_name_field.send_keys(long_name)

        self.start_time_datefield.send_keys('')
        self.start_time_datefield.send_keys(start_date)

        self.start_time_timefield.send_keys('')
        self.start_time_timefield.send_keys(start_time)

        self.end_time_datefield.send_keys('')
        self.end_time_datefield.send_keys(end_date)

        self.end_time_timefield.send_keys('')
        self.end_time_timefield.send_keys(end_time)

        self.short_name_field.clear()
        self.short_name_field.send_keys(short_name)

    def _waitForSaved(self):
        self.waitForCssSelector('.devilry_subjectadmin_periodoverview')

    def test_edit(self):
        self.assertEquals(self.testhelper.sub.periods.count(), 0)
        self._loginTo('subadmin', self.testhelper.sub.id)
        self._waitForFields()
        self.assertFalse(self.savebutton.is_enabled())
        self._set_values(short_name='p1',
                         long_name='Period One',
                         start_date='2000-12-24', start_time='12:00',
                         end_date='2001-11-22', end_time='16:00')
        self.waitForEnabled(self.savebutton)
        self.savebutton.click()
        self._waitForSaved()
        sub = self.testhelper.reload_from_db(self.testhelper.sub)

        self.assertEquals(sub.periods.count(), 1)
        p1 = sub.periods.all()[0]
        self.assertEquals(p1.long_name, 'Period One')
        self.assertEquals(p1.short_name, 'p1')
        self.assertEquals(p1.start_time, datetime(2000, 12, 24, 12, 0))
        self.assertEquals(p1.end_time, datetime(2001, 11, 22, 16, 0))
