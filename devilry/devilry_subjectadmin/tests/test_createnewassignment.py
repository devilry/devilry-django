from datetime import date, timedelta
from time import sleep
import unittest

from selenium.webdriver.common.keys import Keys

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Examiner
from devilry.apps.core.models.deliverytypes import ELECTRONIC, NON_ELECTRONIC
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import ExtJsTestMixin


class TestCreateNewAssignment(SubjectAdminSeleniumTestCase, ExtJsTestMixin):
    def _setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.tomorrow = date.today() + timedelta(days=1)
        self.valid_first_deadline = (self.tomorrow.isoformat(), '15:00')

        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1):ends(6):admin(p1admin)'])
        self.period_id = self.testhelper.sub_p1.id

    def setUp(self):
        try:
            self._setUp()
        except Exception as e:
            print
            print
            print e, type(e), e.__class__
            print
            print
            raise

    def _load(self, period_id=None):
        period_id = period_id or self.period_id
        self.loginTo('p1admin', '/period/{0}/@@create-new-assignment/'.format(period_id))
        self.waitForCssSelector('.devilry_subjectadmin_createnewassignmentform')

    def test_breadcrumb(self):
        self._load()
        breadcrumbtext = self.get_breadcrumbstring('Create new assignment')
        self.assertEquals(breadcrumbtext, ['All my subjects', 'sub.p1', 'Create new assignment'])

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
        self.assertTrue('The server responded with error message <em>403' in self.selenium.page_source)

    def test_form_render_advanced_fieldset(self):
        self._load()
        self.assertTrue('Advanced options' in self.selenium.page_source)

        fieldsetbutton = self.waitForAndFindElementByCssSelector('#advancedOptionsPanel .x-panel-header .linklike')
        sleep(1)
        fieldsetbutton.click()

        self.assertTrue('Anonymous?' in self.selenium.page_source)
        self.assertTrue('If an assignment is anonymous, examiners see' in self.selenium.page_source)
        self.assertTrue('Publishing time' in self.selenium.page_source)

    def _set_value(self, fieldname, value):
        field = self.waitForAndFindElementByCssSelector('input[name={0}]'.format(fieldname))
        field.clear()
        field.send_keys(value)
        field.send_keys(Keys.TAB)

    def _set_names(self, short_name, long_name):
        self._set_value('short_name', 'temp') # NOTE: prevent long_name from automatically set shortname
        self._set_value('long_name', '')
        self._set_value('long_name', long_name)
        self._set_value('short_name', short_name)

    def _set_first_deadline(self, date, time):
        self.extjs_set_datetime_value('.firstDeadlineField', date, time)

    def _expand_advanced(self):
        panel = self.waitForAndFindElementByCssSelector('#advancedOptionsPanel')
        return self.extjs_expand_panel(panel)

    def _set_page1_values(self, short_name='', long_name='',
                          delivery_types=None, first_deadline=None,
                          anonymous=None, publishing_time=None):
        self._set_names(short_name, long_name)
        if first_deadline:
            self._set_first_deadline(first_deadline[0], first_deadline[1])
        if anonymous is not None or publishing_time is not None:
            self._expand_advanced()
            if anonymous is not None:
                self.extjs_set_checkbox_value('.anonymousField', select=anonymous)
            if publishing_time is not None:
                self.extjs_set_datetime_value('.publishingTimeField',
                                              date=publishing_time[0],
                                              time=publishing_time[1])
        if delivery_types is not None:
            if delivery_types == ELECTRONIC:
                self.extjs_click_radiobutton('.deliveryTypesElectronic')
            elif delivery_types == NON_ELECTRONIC:
                self.extjs_click_radiobutton('.deliveryTypesNonElectronic')
            else:
                raise ValueError()

    def _set_page2_values(self, setupstudents_cls=None,
                          setupexaminers_cls=None,
                          only_copy_passing=False,
                          copy_from_label=None):
        if setupstudents_cls:
            self.extjs_click_radiobutton(setupstudents_cls)
        if setupexaminers_cls:
            self.extjs_click_radiobutton(setupexaminers_cls)
        if only_copy_passing:
            self.extjs_set_checkbox_value('.onlyCopyPassingGroupsField', select=True)
        if copy_from_label:
            self.extjs_combobox_select('.copyFromAssignmentIdField',
                                       boundlist_cssselector='.selectsingleassignment_boundlist',
                                       label=copy_from_label)

    def _set_values(self, short_name='', long_name='',
                    delivery_types=None, first_deadline=None,
                    anonymous=None, publishing_time=None,
                    setupstudents_cls=None, setupexaminers_cls=None,
                    only_copy_passing=False, copy_from_label=None):
        self._set_page1_values(short_name=short_name, long_name=long_name,
                               delivery_types=delivery_types,
                               first_deadline=first_deadline,
                               anonymous=anonymous,
                               publishing_time=publishing_time)
        self._click_nextbutton_and_wait_for_pagechange()
        self._set_page2_values(setupstudents_cls=setupstudents_cls,
                               setupexaminers_cls=setupexaminers_cls,
                               only_copy_passing=only_copy_passing,
                               copy_from_label=copy_from_label)

    def _click_createbutton(self):
        createbutton = self.selenium.find_element_by_css_selector('.devilry_extjsextras_createbutton button')
        self.waitForEnabled(createbutton)
        createbutton.click()

    def _click_createbutton_and_wait_for_reload(self):
        self._click_createbutton()
        self.waitForCssSelector('.devilry_subjectadmin_assignmentoverview')

    def _click_nextbutton_and_wait_for_pagechange(self):
        nextbutton = self.selenium.find_element_by_css_selector('.createnewassignmentform_nextbutton button')
        self.waitForEnabled(nextbutton)
        nextbutton.click()
        p2 = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_createnewassignmentform .page2')
        self.waitForDisplayed(p2)

    def test_form_nextbutton(self):
        self._load()

        nextbutton = self.selenium.find_element_by_css_selector('.createnewassignmentform_nextbutton button')
        self.assertFalse(nextbutton.is_enabled())

        self._set_names('', 'Test')
        self.waitForDisabled(nextbutton)
        self._set_value('short_name', 'test')
        self.waitForDisabled(nextbutton)
        self._set_first_deadline(self.tomorrow.isoformat(), '15:00')
        self.waitForEnabled(nextbutton)

    def test_duplicate(self):
        self.testhelper.add_to_path('uni;sub.p1.a1')
        self._load()
        self._set_names('a1', 'A1')
        self._set_first_deadline(self.tomorrow.isoformat(), '15:00')
        self._click_nextbutton_and_wait_for_pagechange()
        self._click_createbutton()
        self.waitForText('Assignment with this Short name and Period already exists')

    def _create_related_student(self, username, candidate_id=None, tags=None):
        user = self.testhelper.create_user(username)
        relatedstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                                          candidate_id=candidate_id)
        if tags:
            relatedstudent.tags = tags
            relatedstudent.save()
        return relatedstudent

    def _create_related_examiner(self, username, tags=None):
        user = self.testhelper.create_user(username)
        relatedexaminer = self.testhelper.sub_p1.relatedexaminer_set.create(user=user)
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

        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=(self.tomorrow.isoformat(), '15:00'))
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.long_name, 'Test')

        self.assertFalse(created.anonymous)
        self.assertEquals(created.delivery_types, ELECTRONIC)
        self.assertEquals(created.assignmentgroups.all().count(), 4)
        student0group = AssignmentGroup.where_is_candidate(self.testhelper.student0).get(parentnode=created.id)
        self.assertEquals(student0group.examiners.all()[0].user, self.testhelper.examiner0)
        self.assertEquals(student0group.deadlines.count(), 1)
        self.assertEquals(student0group.deadlines.all()[0].deadline.date(), self.tomorrow)
        self.assertEquals(student0group.deadlines.all()[0].deadline.time().hour, 15)
        self.assertEquals(student0group.deadlines.all()[0].deadline.time().minute, 0)

    def test_create_anonymous(self):
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         anonymous=True)
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertTrue(created.anonymous)

    def test_setup_no_students(self):
        self._create_related_student('student0', tags=['group1'])
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsDoNotSetupRadio')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 0)
        self.assertEquals(Examiner.objects.filter(assignmentgroup__parentnode=created).count(), 0)

    def test_setup_no_examiners(self):
        self._create_related_student('student0', tags=['group1'])
        self._create_related_examiner('examiner0', tags=['group1'])
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupexaminers_cls='.setupExaminersDoNotSetupRadio')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        self.assertEquals(Examiner.objects.filter(assignmentgroup__parentnode=created).count(), 0)

    def test_setup_copy_from_another(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:pub(1).g1:candidate(notused)')
        self.testhelper.add_to_path('uni;sub.p1.a2:ln(Assignment Two):pub(2).g1:candidate(student1):examiner(examiner1).d1')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyFromAssignmentRadio')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = created.assignmentgroups.all()[0]
        self.assertEquals(group.candidates.all()[0].student, self.testhelper.student1)
        self.assertEquals(group.examiners.all()[0].user, self.testhelper.examiner1)

    def test_setup_copy_from_another_noexaminers(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment One).g1:candidate(student1):examiner(examiner1).d1')
        g1 = self.testhelper.sub_p1_a1_g1
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyFromAssignmentRadio',
                         setupexaminers_cls='.setupExaminersDoNotSetupRadio')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = created.assignmentgroups.all()[0]
        self.assertEquals(group.examiners.count(), 0)

    def test_setup_copy_from_another_onlypassing(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment One).g1:candidate(student1):examiner(examiner1).d1')
        g1 = self.testhelper.sub_p1_a1_g1
        self.testhelper.add_delivery(g1, {'a.py': ['print ', 'yeh']})
        self.testhelper.add_feedback(g1, verdict={'grade': 'A', 'points': 10, 'is_passing_grade': True})

        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2):examiner(examiner1).d1')
        g2 = self.testhelper.sub_p1_a1_g2
        self.testhelper.add_delivery(g2, {'f.py': ['print ', 'meh']})
        self.testhelper.add_feedback(g2, verdict={'grade': 'F', 'points': 1, 'is_passing_grade': False})

        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyFromAssignmentRadio',
                         only_copy_passing=True)
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = created.assignmentgroups.all()[0]
        self.assertEquals(group.candidates.all()[0].student, self.testhelper.student1)

    def test_setup_copy_from_another_specify_other(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment One):pub(2).g1:candidate(selectedstud).d1')
        self.testhelper.add_to_path('uni;sub.p1.a2:ln(Assignment Two):pub(3).g1:candidate(ignored).d1')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyFromAssignmentRadio',
                         copy_from_label='Assignment One')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = created.assignmentgroups.all()[0]
        self.assertEquals(group.candidates.all()[0].student, self.testhelper.selectedstud)

    def test_setup_nonelectronic(self):
        self._create_related_student('student0', tags=['group1'])
        self._create_related_examiner('examiner0', tags=['group1'])
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         delivery_types=NON_ELECTRONIC)
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.long_name, 'Test')

        self.assertFalse(created.anonymous)
        self.assertEquals(created.delivery_types, NON_ELECTRONIC)
        self.assertEquals(created.assignmentgroups.all().count(), 1)
        group = created.assignmentgroups.all()[0]
        self.assertEquals(group.examiners.all()[0].user, self.testhelper.examiner0)
        self.assertEquals(group.candidates.all()[0].student, self.testhelper.student0)

    def test_nonelectronic_hide_first_deadline_field(self):
        self._load()
        firstDeadlineField = self.waitForAndFindElementByCssSelector('.firstDeadlineField')
        self.waitForDisplayed(firstDeadlineField)
        self._set_page1_values(short_name='sometest', long_name='Test',
                               delivery_types=NON_ELECTRONIC)
        self.waitForNotDisplayed(firstDeadlineField)
        self._set_page1_values(short_name='sometest', long_name='Test',
                               delivery_types=ELECTRONIC)
        self.waitForDisplayed(firstDeadlineField)

    def test_page2_nocopyfrom_when_firstinperiod(self):
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline)
        copyFromPanel = self.waitForAndFindElementByCssSelector('.copyFromAssignmentIdField')
        self.assertFalse(copyFromPanel.is_displayed())

    def test_page2_showhide_setupexaminers(self):
        self.testhelper.add_to_path('uni;sub.p1.a1')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline)
        setupExaminersContainer = self.waitForAndFindElementByCssSelector('.setupExaminersContainer')
        self.waitForDisplayed(setupExaminersContainer)
        self._set_page2_values(setupstudents_cls='.setupStudentsDoNotSetupRadio')
        self.waitForNotDisplayed(setupExaminersContainer)
        self._set_page2_values(setupstudents_cls='.setupStudentsAllRelatedRadio')
        self.waitForDisplayed(setupExaminersContainer)

    def test_page2_toggle_allrelated_and_copyfromassignment(self):
        self.testhelper.add_to_path('uni;sub.p1.a1')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline)

        setupExaminersByTagsRadio = self.waitForAndFindElementByCssSelector('.setupExaminersByTagsRadio')
        setupExaminersCopyFromAssignmentRadio = self.waitForAndFindElementByCssSelector('.setupExaminersCopyFromAssignmentRadio')
        self.waitForDisplayed(setupExaminersByTagsRadio)
        self.waitForNotDisplayed(setupExaminersCopyFromAssignmentRadio)

        self._set_page2_values(setupstudents_cls='.setupStudentsCopyFromAssignmentRadio')
        self.waitForDisplayed(setupExaminersCopyFromAssignmentRadio)
        self.waitForNotDisplayed(setupExaminersByTagsRadio)

        self._set_page2_values(setupstudents_cls='.setupStudentsAllRelatedRadio')
        self.waitForDisplayed(setupExaminersByTagsRadio)
        self.waitForNotDisplayed(setupExaminersCopyFromAssignmentRadio)

    def test_page2_copyfromassignment_examinerlabelchange(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment One):pub(2)')
        self.testhelper.add_to_path('uni;sub.p1.a2:ln(Assignment Two):pub(3)')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyFromAssignmentRadio')

        setupExaminersCopyFromAssignmentRadio = self.waitForAndFindElementByCssSelector('.setupExaminersCopyFromAssignmentRadio')
        self.waitForText('Assignment Two', within=setupExaminersCopyFromAssignmentRadio)

        self._set_page2_values(copy_from_label='Assignment One')
        self.waitForText('Assignment One', within=setupExaminersCopyFromAssignmentRadio)

    def test_autoset_names(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment 1)')
        self._load()
        info = self.waitForAndFindElementByCssSelector('.devilry_extjsextras_floatingalertmessagelist .alert-info')
        self.assertIn('values for: Name', info.text)

    def _minuteprecise_datetime(self, datetimeobj):
        return datetimeobj.replace(second=0, microsecond=0, tzinfo=None)

    def _waitForAndGetFirstDeadlineFieldValue(self):
        self.waitFor(self.selenium, lambda s: self.extjs_get_datetime_value('.firstDeadlineField') != None)
        deadline = self.extjs_get_datetime_value('.firstDeadlineField')
        if deadline:
            return self._minuteprecise_datetime(deadline)
        else:
            return deadline

    def test_autoset_first_deadline(self):
        self.testhelper.add_to_path('uni;sub.p1.a:first_deadline(25)')
        self.testhelper.add_to_path('uni;sub.p1.b:first_deadline(35)')
        expected_deadline = self._minuteprecise_datetime(self.testhelper.sub_p1_b.first_deadline + timedelta(days=10))

        self._load()
        info = self.waitForAndFindElementByCssSelector('.devilry_extjsextras_floatingalertmessagelist .alert-info')
        self.assertIn('Submission date', info.text)
        first_deadline = self._waitForAndGetFirstDeadlineFieldValue()
        self.assertEquals(expected_deadline, first_deadline)

    @unittest.skip('This fails when running as part of the test suite, but not when run alone')
    def test_autoset_first_deadline_2weeks_off(self):
        self.testhelper.add_to_path('uni;sub.p1.a:first_deadline(15)')
        self.testhelper.add_to_path('uni;sub.p1.b:first_deadline(20)')
        self.testhelper.add_to_path('uni;sub.p1.c:first_deadline(25)')
        expected_deadline = self._minuteprecise_datetime(self.testhelper.sub_p1_c.first_deadline + timedelta(days=10))

        self._load()
        info = self.waitForAndFindElementByCssSelector('.devilry_extjsextras_floatingalertmessagelist .alert-info')
        self.assertIn('Submission date', info.text)
        self._waitForAndGetFirstDeadlineFieldValue()
        self.waitFor(
            self.selenium,
            lambda s: self.extjs_get_datetime_value('.firstDeadlineField') == expected_deadline,
            timeout=8)

    def test_autoset_first_deadline_ignore_empty(self):
        self.testhelper.add_to_path('uni;sub.p1.a:first_deadline(25)')
        self.testhelper.add_to_path('uni;sub.p1.b') # Should be ignored
        self.testhelper.add_to_path('uni;sub.p1.c:first_deadline(35)')
        expected_deadline = self._minuteprecise_datetime(self.testhelper.sub_p1_c.first_deadline + timedelta(days=10))

        self._load()
        info = self.waitForAndFindElementByCssSelector('.devilry_extjsextras_floatingalertmessagelist .alert-info')
        self.assertIn('Submission date', info.text)
        first_deadline = self._waitForAndGetFirstDeadlineFieldValue()
        self.assertEquals(expected_deadline, first_deadline)
