from datetime import date, timedelta
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Examiner
from selenium.webdriver.common.keys import Keys

from .base import SubjectAdminSeleniumTestCase
from .base import ExtJsTestMixin


class TestCreateNewAssignment(SubjectAdminSeleniumTestCase, ExtJsTestMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.tomorrow = date.today() + timedelta(days=1)
        self.valid_first_deadline = (self.tomorrow.isoformat(), '15:00')

        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-1):ends(6):admin(p1admin)'])
        self.period_id = self.testhelper.sub_p1.id

    def _load(self, period_id=None):
        period_id = period_id or self.period_id
        self.loginTo('p1admin', '/period/{0}/@@create-new-assignment/'.format(period_id))
        self.waitForCssSelector('.devilry_subjectadmin_createnewassignmentform')

    def test_breadcrumb(self):
        self._load()
        breadcrumbtext = self.get_breadcrumbstring('Create new assignment')
        self.assertEquals(breadcrumbtext, ['All subjects', 'sub.p1', 'Create new assignment'])

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

        fieldsetbutton = self.selenium.find_element_by_css_selector('#advancedOptionsPanel .x-panel-header')
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
        self._set_value('long_name', long_name)
        self._set_value('short_name', short_name)

    def _set_first_deadline(self, date, time):
        self.extjs_set_datetime_values('.firstDeadlineField', date, time)

    def _expand_advanced(self):
        panel = self.waitForAndFindElementByCssSelector('#advancedOptionsPanel')
        return self.extjs_expand_panel(panel)

    def _set_page1_values(self, short_name='', long_name='',
                          delivery_types='', first_deadline=None,
                          anonymous=None, publishing_time=None):
        self._set_names(short_name, long_name)
        if first_deadline:
            self._set_first_deadline(first_deadline[0], first_deadline[1])
        if anonymous != None or publishing_time!=None:
            self._expand_advanced()
            if anonymous != None:
                self.extjs_set_checkbox_value('.anonymousField', select=anonymous)
            if publishing_time != None:
                self.extjs_set_datetime_values('.publishingTimeField',
                                               date=publishing_time[0],
                                               time=publishing_time[1])
    def _set_page2_values(self, setupstudents_cls=None,
                          setupexaminers_cls=None,
                          only_copy_passing=False):
        if setupstudents_cls:
            self.extjs_click_radiobutton(setupstudents_cls)
        if setupexaminers_cls:
            self.extjs_click_radiobutton(setupexaminers_cls)
        if only_copy_passing:
            self.extjs_set_checkbox_value('.onlyCopyPassingGroupsField', select=True)

    def _set_values(self, short_name='', long_name='',
                    delivery_types='', first_deadline=None,
                    anonymous=None, publishing_time=None,
                    setupstudents_cls=None, setupexaminers_cls=None,
                    only_copy_passing=False):
        self._set_page1_values(short_name=short_name, long_name=long_name,
                               delivery_types=delivery_types,
                               first_deadline=first_deadline,
                               anonymous=anonymous,
                               publishing_time=publishing_time)
        self._click_nextbutton_and_wait_for_pagechange()
        self._set_page2_values(setupstudents_cls=setupstudents_cls,
                               setupexaminers_cls=setupexaminers_cls,
                               only_copy_passing=only_copy_passing)


    def _click_createbutton_and_wait_for_reload(self):
        createbutton = self.selenium.find_element_by_css_selector('.devilry_extjsextras_createbutton button')
        self.waitForEnabled(createbutton)
        createbutton.click()
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

    def _save_directly_from_pageone(self):
        self._click_nextbutton_and_wait_for_pagechange()
        self._click_createbutton_and_wait_for_reload()

    def test_duplicate(self):
        self.testhelper.add_to_path('uni;sub.p1.a1')
        self._load()
        self._set_names('a1', 'A1')
        self._set_first_deadline(self.tomorrow.isoformat(), '15:00')
        self._save_directly_from_pageone()
        self.waitForCssSelector('.devilry_extjsextras_alertmessagelist')
        self.assertTrue('Assignment with this Short name and Period already exists' in self.selenium.page_source)

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
                         setupstudents_cls='.setupStudentsCopyRadio')
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
                         setupstudents_cls='.setupStudentsCopyRadio',
                         setupexaminers_cls='.setupExaminersDoNotSetupRadio')
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = AssignmentGroup.where_is_candidate(self.testhelper.student1).get(parentnode=created.id)
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
                         setupstudents_cls='.setupStudentsCopyRadio',
                         only_copy_passing=True)
        self._click_createbutton_and_wait_for_reload()
        created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        self.assertEquals(created.assignmentgroups.count(), 1)
        group = AssignmentGroup.where_is_candidate(self.testhelper.student1).get(parentnode=created.id)
        self.assertEquals(group.candidates.all()[0].student, self.testhelper.student1)

    def test_setup_copy_from_another_specify_other(self):
        self.testhelper.add_to_path('uni;sub.p1.a1:ln(Assignment One):pub(2).g1:candidate(student1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a2:ln(Assignment Two):pub(3).g1:candidate(student1).d1')
        self._load()
        self._set_values(short_name='sometest', long_name='Test',
                         first_deadline=self.valid_first_deadline,
                         setupstudents_cls='.setupStudentsCopyRadio',
                         copy_from='Assignment One')
        raw_input('1')
        #self._click_createbutton_and_wait_for_reload()
        #created = Assignment.objects.get(parentnode__id=self.period_id, short_name='sometest')
        #self.assertEquals(created.assignmentgroups.count(), 1)
        #group = AssignmentGroup.where_is_candidate(self.testhelper.student1).get(parentnode=created.id)
        #self.assertEquals(group.examiners.all()[0].user, self.testhelper.examiner1)


    #def test_setup_nonelectronic(self):
        #pass
