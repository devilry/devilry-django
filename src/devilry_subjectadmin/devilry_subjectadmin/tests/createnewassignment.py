from datetime import date, timedelta
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Assignment, AssignmentGroup
from selenium.webdriver.common.keys import Keys

from .base import SubjectAdminSeleniumTestCase


class TestCreateNewAssignment(SubjectAdminSeleniumTestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.tomorrow = date.today() + timedelta(days=1)

        self.testhelper.add(nodes='uni',
                            subjects=['duck1100'],
                            periods=['periodone:begins(-1):ends(6):admin(periodoneadmin)'])
        self.login('periodoneadmin')
        self.period_id = self.testhelper.duck1100_periodone.id

    def _load(self, period_id=None):
        period_id = period_id or self.period_id
        self.browseTo('/period/{0}/@@create-new-assignment/'.format(period_id))
        self.waitForCssSelector('.devilry_subjectadmin_createnewassignmentform')

    def test_form_render(self):
        self._load()

        self.assertTrue('Create new assignment' in self.selenium.page_source)

        self.assertTrue('Long name' in self.selenium.page_source)
        self.assertTrue('Example: Obligatory assignment one' in self.selenium.page_source)
        self.assertTrue('Short name' in self.selenium.page_source)
        self.assertTrue('Example: oblig-1' in self.selenium.page_source)
        self.assertTrue('Choose a long and a short name' in self.selenium.page_source)
        self.assertTrue('How do students add deliveries?' in self.selenium.page_source)

    def test_invalid_period(self):
        self._load('1001666')
        self.waitForCssSelector('.devilry_subjectadmin_createnewassignmentform')
        self.assertTrue('Period 1001666 could not be loaded.' in self.selenium.page_source)

    def test_form_render_advanced_fieldset(self):
        self._load()
        self.assertTrue('Advanced options' in self.selenium.page_source)

        fieldsetbutton = self.selenium.find_element_by_css_selector('#advancedOptionsPanel .x-panel-header')
        fieldsetbutton.click()

        self.assertTrue('Anonymous?' in self.selenium.page_source)
        self.assertTrue('If an assignment is anonymous, examiners see' in self.selenium.page_source)
        self.assertTrue('Publishing time' in self.selenium.page_source)


    def _set_value(self, fieldname, value):
        field = self.selenium.find_element_by_css_selector('input[name={0}]'.format(fieldname))
        field.clear()
        field.send_keys(value)
        field.send_keys(Keys.TAB)

    def _set_names(self, short_name, long_name):
        self._set_value('short_name', 'temp') # NOTE: prevent long_name from automatically set shortname
        self._set_value('long_name', long_name)
        self._set_value('short_name', short_name)

    def _set_datetime_value(self, fieldclass, field, value):
        field = self.selenium.find_element_by_css_selector('.{fieldclass} .devilry_extjsextras_{field}field input[type=text]'.format(fieldclass=fieldclass,
                                                                                                                          field=field))
        field.send_keys(value)
        field.send_keys(Keys.TAB)

    def _set_first_deadline(self, date, time):
        self._set_datetime_value('first_deadline', 'date', date)
        self._set_datetime_value('first_deadline', 'time', time)

    def test_form_nextbutton(self):
        self._load()

        nextbutton = self.selenium.find_element_by_css_selector('.createnewassignmentform_nextbutton button')
        self.assertFalse(nextbutton.is_enabled())

        # Make sure the next button is clickable after both short and long names are entered.
        self._set_names('', 'Test')
        self.assertFalse(nextbutton.is_enabled())

        self._set_value('short_name', 'test')
        self.waitForEnabled(nextbutton)

    def _click_createbutton(self):
        createbutton = self.selenium.find_element_by_css_selector('.devilry_extjsextras_createbutton button')
        self.waitForEnabled(createbutton)
        createbutton.click()

    def _click_nextbutton(self):
        nextbutton = self.selenium.find_element_by_css_selector('.createnewassignmentform_nextbutton button')
        self.waitForEnabled(nextbutton)
        nextbutton.click()

    def _save_directly_from_pageone(self):
        self._click_nextbutton()
        self._click_createbutton()

    def test_duplicate(self):
        self.testhelper.add_to_path('uni;duck1100.periodone.a1')
        self._load()
        self._set_names('a1', 'A1')
        self._set_first_deadline(self.tomorrow.isoformat(), '15:00')
        self._save_directly_from_pageone()
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('Assignment with this Short name and Period already exists' in self.selenium.page_source)

    def test_success(self):
        self._load()

        self._set_names('sometest', 'Test')
        self._set_first_deadline(self.tomorrow.isoformat(), '15:00')
        self._save_directly_from_pageone()

        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.long_name, 'Test')
        return created


    def _create_related_student(self, username, candidate_id=None, tags=None):
        user = self.testhelper.create_user(username)
        relatedstudent = self.testhelper.duck1100_periodone.relatedstudent_set.create(user=user,
                                                                          candidate_id=candidate_id)
        if tags:
            relatedstudent.tags = tags
            relatedstudent.save()
        return relatedstudent

    def _create_related_examiner(self, username, tags=None):
        user = self.testhelper.create_user(username)
        relatedexaminer = self.testhelper.duck1100_periodone.relatedexaminer_set.create(user=user)
        if tags:
            relatedexaminer.tags = tags
            relatedexaminer.save()
        return relatedexaminer

    def test_create_with_related(self):
        self._create_related_student('student0', tags=['group1'])
        self._create_related_student('student1', tags=['group1'])
        self._create_related_student('student2', tags=['group1'])
        self._create_related_student('student3', tags=['group2'])
        self._create_related_examiner('examiner0', tags=['group1'])
        created = self.test_success()
        self.assertEquals(created.assignmentgroups.all().count(), 4)
        student0group = AssignmentGroup.where_is_candidate(self.testhelper.student0).get(parentnode=created.id)
        self.assertEquals(student0group.examiners.all()[0].user, self.testhelper.examiner0)
        self.assertEquals(student0group.deadlines.count(), 1)
        self.assertEquals(student0group.deadlines.all()[0].deadline.date(), self.tomorrow)
        self.assertEquals(student0group.deadlines.all()[0].deadline.time().hour, 15)
        self.assertEquals(student0group.deadlines.all()[0].deadline.time().minute, 0)

    def test_breadcrumb(self):
        self._load()
        breadcrumbtext = self.get_breadcrumbstring('Create new assignment')
        self.assertEquals(breadcrumbtext, ['All subjects', 'duck1100', 'periodone', 'Create new assignment'])
