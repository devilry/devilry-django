from datetime import datetime, timedelta
from time import sleep

from selenium.common.exceptions import StaleElementReferenceException

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import WaitForAlertMessageMixin


class TestManageSingleGroupMixin(object):
    DELIVERY_TYPES = 'electronic'

    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:begins(-2):ends(6)'],
                            assignments=['a1:admin(a1admin):delivery_types({0})'.format(self.DELIVERY_TYPES)])
        self.assignment = self.testhelper.sub_p1_a1

    def browseToAndSelectAs(self, username, select_group):
        path = '/assignment/{0}/@@manage-students/@@select/{1}'.format(self.assignment.id,
                                                                       select_group.id)
        self.loginTo(username, path)
        return self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupview')

    def create_group(self, groupspec):
        self.testhelper.add_to_path('uni;sub.p1.a1.{0}'.format(groupspec))
        groupname = groupspec.split('.')[0].split(':')[0]
        return getattr(self.testhelper, 'sub_p1_a1_{0}'.format(groupname))

    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_singlegroupview {0}'.format(cssselector))
    def find_elements(self, cssselector):
        return self.selenium.find_elements_by_css_selector('.devilry_subjectadmin_singlegroupview {0}'.format(cssselector))

    def find_listofgroups_rows(self, selected_only=False):
        cssselector = '.devilry_subjectadmin_listofgroups .x-grid-row'
        if selected_only:
            cssselector += '-selected'
        return self.selenium.find_elements_by_css_selector(cssselector)


class TestManageSingleGroupOverview(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.create_group('g2:candidate(student2)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.browseToAndSelectAs('a1admin', g1)
        meta = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupmetainfo')
        sleep(1)
        self.assertEquals(meta.text.strip(), 'Waiting for deliveries')
        self.assertEquals(len(meta.find_elements_by_css_selector('.status-waiting-for-deliveries')), 1)

    def test_no_deadlines(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', g1)
        meta = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupmetainfo')
        sleep(1)
        self.assertEquals(meta.text.strip(), 'no-deadlines')
        self.assertEquals(len(meta.find_elements_by_css_selector('.status-no-deadlines')), 1)

    def test_passing_grade(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_feedback(g1, verdict={'grade': 'C', 'points': 85, 'is_passing_grade': True},
                                     rendered_view="Hello world")

        self.browseToAndSelectAs('a1admin', g1)
        meta = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupmetainfo')
        sleep(1)
        self.assertEquals(len(meta.find_elements_by_css_selector('.status-corrected')), 1)
        self.assertEquals(len(meta.find_elements_by_css_selector('.passing_grade')), 1)
        self.assertEquals(len(meta.find_elements_by_css_selector('.failing_grade')), 0)
        self.assertEquals(meta.find_element_by_css_selector('.passing_grade').text.strip(), 'Passed')
        self.assertEquals(meta.find_element_by_css_selector('.grade').text.strip(), '(C)')
        self.assertEquals(meta.find_element_by_css_selector('.points').text.strip(), '(Points: 85)')

    def test_failing_grade(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_feedback(g1, verdict={'grade': 'F', 'points': 2, 'is_passing_grade': False},
                                     rendered_view="Hello world")

        self.browseToAndSelectAs('a1admin', g1)
        meta = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupmetainfo')
        sleep(1)
        self.assertEquals(len(meta.find_elements_by_css_selector('.status-corrected')), 1)
        self.assertEquals(len(meta.find_elements_by_css_selector('.passing_grade')), 0)
        self.assertEquals(len(meta.find_elements_by_css_selector('.failing_grade')), 1)
        self.assertEquals(meta.find_element_by_css_selector('.failing_grade').text.strip(), 'Failed')
        self.assertEquals(meta.find_element_by_css_selector('.grade').text.strip(), '(F)')
        self.assertEquals(meta.find_element_by_css_selector('.points').text.strip(), '(Points: 2)')

    def test_examinerbox_notexaminer(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.browseToAndSelectAs('a1admin', g1)
        examinerRoleBox = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupview .examinerRoleBox')

        text = self.waitForAndFindElementByCssSelector('.text', within=examinerRoleBox)
        self.assertTrue(text.text.strip().startswith('You need to be examiner for this group if you want to provide feedback'))

        button = self.waitForAndFindElementByCssSelector('a.btn', within=examinerRoleBox)
        self.assertEquals(button.text.strip(), 'Make me examiner')
        button.click()
        self.waitForText('Added you as examiner for: student1')
        self.waitFor(self.selenium, lambda s: g1.examiners.count() == 1, timeout=2)
        added_examiner = g1.examiners.all().first()
        self.assertEquals(added_examiner.user, self.testhelper.a1admin)

    def test_examinerbox_isexaminer(self):
        g1 = self.create_group('g1:candidate(student1):examiner(a1admin)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.browseToAndSelectAs('a1admin', g1)
        examinerRoleBox = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupview .examinerRoleBox')

        text = self.waitForAndFindElementByCssSelector('.text', within=examinerRoleBox)
        self.assertTrue(text.text.strip().startswith('You are examiner for this group'))
        button = self.waitForAndFindElementByCssSelector('a.btn', within=examinerRoleBox)
        self.assertEquals(button.text.strip(), 'Create/edit feedback')

    def test_examinerbox_notpublished(self):
        self.testhelper.sub_p1_a1.publishing_time = datetime.now() + timedelta(days=2)
        self.testhelper.sub_p1_a1.save()
        g1 = self.create_group('g1:candidate(student1):examiner(a1admin)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.browseToAndSelectAs('a1admin', g1)
        examinerRoleBox = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_singlegroupview .examinerRoleBox')
        self.waitForText('This assignment will be published in', within=examinerRoleBox)


class TestManageSingleGroupStudents(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def _find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_studentsingroupgrid .x-grid-row')

    def test_render(self):
        self.testhelper.create_user('student1', fullname='Student One')
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsonsingle')
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        fullname = self.find_element('.studentsingroupgrid_meta_student1 .fullname')
        username = self.find_element('.studentsingroupgrid_meta_student1 .username')
        self.assertTrue(fullname.text.strip(), 'Student One')
        self.assertTrue(username.text.strip(), 'student1')

    def test_missing_fullname(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_managestudentsonsingle')
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        missing = self.find_element('.studentsingroupgrid_meta_student1 .fullname .nofullname')
        username = self.find_element('.studentsingroupgrid_meta_student1 .username')
        self.assertTrue(missing.text.strip(), 'Full name missing')
        self.assertTrue(username.text.strip(), 'student1')

    def _pop_by_username(self, username):
        cssselector = '.studentsingroupgrid_pop_{0}'.format(username)
        self.waitForCssSelector(cssselector)
        self.find_element(cssselector).click()

        # Confirm delete
        self.waitForCssSelector('#single_students_confirm_pop .okbutton')
        okbutton = self.find_element('#single_students_confirm_pop .okbutton')
        self.waitFor(okbutton, lambda b: okbutton.is_displayed())
        okbutton.click()

        # After pop, the original and the split group will be marked in the multi-view
        def twoSelected(s):
            return len(self.find_listofgroups_rows(selected_only=True)) == 2
        self.waitFor(self.selenium, twoSelected)

    def test_pop(self):
        g1 = self.create_group('g1:candidate(student1,student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_pop')), 2)
        self._pop_by_username('student2')

    def test_pop_cancel(self):
        g1 = self.create_group('g1:candidate(student1,student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_pop')), 2)

        cssselector = '.studentsingroupgrid_pop_student1'
        self.waitForCssSelector(cssselector)
        self.find_element(cssselector).click()

        # Cancel
        cancelbutton = self.find_element('#single_students_confirm_pop .cancelbutton')
        self.waitFor(cancelbutton, lambda b: cancelbutton.is_displayed())
        cancelbutton.click()
        meta = self.find_element('.studentsingroupgrid_meta_student1')
        self.waitFor(meta, lambda m: meta.is_displayed())


class TestManageSingleGroupExaminers(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def _find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_examinersingroupgrid .x-grid-row')

    def test_render(self):
        self.testhelper.create_user('examiner1', fullname='Examiner One')
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_manageexaminersonsingle')
        self.waitForCssSelector('.examinersingroupgrid_meta_examiner1')
        fullname = self.find_element('.examinersingroupgrid_meta_examiner1 .fullname')
        username = self.find_element('.examinersingroupgrid_meta_examiner1 .username')
        self.assertTrue(fullname.text.strip(), 'Examiner One')
        self.assertTrue(username.text.strip(), 'examiner1')

    def test_missing_fullname(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_manageexaminersonsingle')
        self.waitForCssSelector('.examinersingroupgrid_meta_examiner1')
        missing = self.find_element('.examinersingroupgrid_meta_examiner1 .fullname .nofullname')
        username = self.find_element('.examinersingroupgrid_meta_examiner1 .username')
        self.assertTrue(missing.text.strip(), 'Full name missing')
        self.assertTrue(username.text.strip(), 'examiner1')

    def _create_related_examiner(self, username, fullname=None):
        user = self.testhelper.create_user(username, fullname=fullname)
        self.assignment.parentnode.relatedexaminer_set.create(user=user)

    def _find_relatedexaminer_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_selectexaminersgrid .x-grid-row')

    def _get_relatedexaminer_row_by_username(self, username):
        for row in self._find_relatedexaminer_gridrows():
            matches = row.find_elements_by_css_selector('.examiner_username_{username}'.format(username=username))
            if len(matches) > 0:
                return row

    def _click_relatedexaminerchecker_by_username(self, username):
        self._get_relatedexaminer_row_by_username(username).find_element_by_css_selector('.x-grid-row-checker').click()

    def _has_reloaded(self, ignored):
        # Since the #single_examiners_help_and_buttons_container is invisible on the
        # save, it will not become visible again until reloaded
        panels = self.find_elements('#single_examiners_help_and_buttons_container')
        if panels:
            try:
                return panels[0].is_displayed()
            except StaleElementReferenceException:
                pass
        return False

    def _click_edit_examiners_button(self):
        setbutton = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_manageexaminersonsingle .containerwithedittitle a.edit_link')
        sleep(1)
        setbutton.click()

    def _set_examiners(self, group, click_examiners):
        self.browseToAndSelectAs('a1admin', group)
        self._click_edit_examiners_button()

        # Select newexaminer and newexaminer2, and save
        panel = self.find_element('#single_set_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        for examiner in click_examiners:
            self.waitForCssSelector('.examiner_username_{0}'.format(examiner))
        for examiner in click_examiners:
            self._click_relatedexaminerchecker_by_username(examiner)
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()
        self.waitFor(self.selenium, lambda s: 'Changed examiners of' in self.selenium.page_source)

    def test_set(self):
        self._create_related_examiner('newexaminer', fullname='New Examiner')
        self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self._set_examiners(g1, ['newexaminer', 'newexaminer2'])

        # Check the results
        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(set([e.user.username for e in g1.examiners.all()]),
                          set(['newexaminer', 'newexaminer2']))

    def test_clear(self):
        self._create_related_examiner('examiner1')
        self._create_related_examiner('examiner2')
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1,examiner2)')
        self._set_examiners(g1, click_examiners=['examiner1', 'examiner2'])  # Should deselect them both
        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(g1.examiners.count(), 0)

    def test_set_cancel(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1,examiner2)')
        self.browseToAndSelectAs('a1admin', g1)
        self._click_edit_examiners_button()

        # Cancel
        cancelbutton = self.find_element('#single_set_examiners_panel .cancelbutton')
        self.waitFor(cancelbutton, lambda b: cancelbutton.is_displayed())
        cancelbutton.click()
        meta = self.find_element('.examinersingroupgrid_meta_examiner1')
        self.waitFor(meta, lambda m: meta.is_displayed())


class TestManageSingleGroupTags(TestManageSingleGroupMixin, SubjectAdminSeleniumTestCase):
    def _find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_tagsingroupgrid .x-grid-row')

    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g1.tags.create(tag='a')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.devilry_subjectadmin_managetagsonsingle')
        self.waitForCssSelector('.tagsingroupgrid_tag_a')
        tag = self.find_element('.tagsingroupgrid_tag_a')
        self.assertTrue(tag.text.strip(), 'a')

    def _click_edit_tags_button(self):
        setbutton = self.waitForAndFindElementByCssSelector('.devilry_subjectadmin_managetagsonsingle .containerwithedittitle a.edit_link')
        sleep(1)
        setbutton.click()

    def _set_tags(self, group, tags):
        # Select newtag and newtag2, and save
        panel = self.find_element('#single_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        inputfield = panel.find_element_by_css_selector('textarea')
        inputfield.clear()
        inputfield.send_keys(tags)
        okbutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()
        self.waitFor(self.selenium, lambda s: 'Saved the following tags for' in self.selenium.page_source)

    def test_set(self):
        g1 = self.create_group('g1:candidate(student1)')
        g1.tags.create(tag='a')
        g1.tags.create(tag='b')
        self.browseToAndSelectAs('a1admin', g1)
        self._click_edit_tags_button()
        self._set_tags(g1, 'newtag1,newtag2')

        # Check the results
        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(set([t.tag for t in g1.tags.all()]),
                          set(['newtag1', 'newtag2']))

    def test_current_tags_present_on_show(self):
        g1 = self.create_group('g1:candidate(student1)')
        g1.tags.create(tag='supertagone')
        g1.tags.create(tag='supertagtwo')
        panel = self.browseToAndSelectAs('a1admin', g1)
        self.waitForText('supertagone', within=panel)
        self.waitForText('supertagtwo', within=panel)
        self._click_edit_tags_button()
        panel = self.find_element('#single_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        inputfield = panel.find_element_by_css_selector('textarea')
        self.waitFor(inputfield, lambda i: i.get_attribute('value') == 'supertagone,supertagtwo')

    def test_clear(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self._click_edit_tags_button()
        self._set_tags(g1, '')
        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(g1.tags.count(), 0)

    def test_set_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g1.tags.create(tag='a')
        self.browseToAndSelectAs('a1admin', g1)
        self._click_edit_tags_button()

        # Cancel
        cancelbutton = self.find_element('#single_set_tags_panel .choosetags_cancelbutton')
        self.waitFor(cancelbutton, lambda b: cancelbutton.is_displayed())
        cancelbutton.click()
        meta = self.find_element('.tagsingroupgrid_tag_a')
        self.waitFor(meta, lambda m: meta.is_displayed())


class DeadlineTestMixin(object):
    def getDeliveryCount(self, deadline):
        deliverycount_el = deadline.find_element_by_css_selector('.deadlineheader .deliverycount')
        return int(deliverycount_el.text.strip())

    def click_header(self, deadline):
        header = deadline.find_element_by_css_selector('.x-panel-header')
        header.click()

    def show_deadline(self, deadline):
        self.click_header(deadline)
        self.waitFor(deadline, lambda d: deadline.find_element_by_css_selector('.x-panel-body').is_displayed())

    def get_deliveries(self, deadline):
        return deadline.find_elements_by_css_selector('.devilry_subjectadmin_admingroupinfo_delivery')

    def waitForDeadlineCount(self, count):
        deadlinescontainer = self.waitForAndFindElementByCssSelector(
            '.devilry_subjectadmin_admingroupinfo_deadlinescontainer')

        def get_deadlines():
            return deadlinescontainer.find_elements_by_css_selector('.devilry_subjectadmin_admingroupinfo_deadline')

        # print
        # print count
        # raw_input('x:')
        self.waitFor(deadlinescontainer, lambda d: len(get_deadlines()) == count)
        return get_deadlines()


class TestManageSingleGroupDeadlinesAndDeliveries(DeadlineTestMixin, TestManageSingleGroupMixin,
                                                  SubjectAdminSeleniumTestCase):

    def _isInTheFuture(self, deadline):
        return len(deadline.find_elements_by_css_selector('.deadlineheader .in_the_future .text-success')) == 1

    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(1)')
        self.testhelper.add_delivery(g1, {'a.py': ['print ', 'meh']})
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_delivery(g1, {'c.py': ['print ', 'meh']})

        self.browseToAndSelectAs('a1admin', g1)
        deadlines = self.waitForDeadlineCount(2)

        self.assertEquals(self.getDeliveryCount(deadlines[0]), 2)
        self.assertTrue(self._isInTheFuture(deadlines[0]))
        self.assertEquals(self.getDeliveryCount(deadlines[1]), 1)
        self.assertFalse(self._isInTheFuture(deadlines[1]))

    def test_deadlinerender(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_delivery(g1, {'c.py': ['print ', 'meh']})

        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.show_deadline(deadline)
        deliveries = self.get_deliveries(deadline)
        self.assertEquals(len(deliveries), 2)

    def test_delivery_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})

        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.show_deadline(deadline)
        delivery = self.get_deliveries(deadline)[0]

        self.assertEquals(len(delivery.find_elements_by_css_selector('.no_feedback')), 1)
        made_by = delivery.find_element_by_css_selector('.deliverymadebyblock .madeby_displayname').text.strip()
        self.assertEquals(made_by, 'student1')

        # Make sure we render all the blocks (could mess up if we handle non-electronic incorrectly)
        for cls in ('.gradeblock', '.activefeedbackblock', '.timeofdeliveryblock', '.deliverymadebyblock', '.fileblock'):
            self.assertEquals(len(delivery.find_elements_by_css_selector(cls)), 1)

    def test_delivery_feedback(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_feedback(g1, verdict={'grade': 'C', 'points': 85, 'is_passing_grade': True},
                                     rendered_view="Hello world")

        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.show_deadline(deadline)
        delivery = self.get_deliveries(deadline)[0]

        self.assertEquals(len(delivery.find_elements_by_css_selector('.no_feedback')), 0)
        feedback = delivery.find_element_by_css_selector('.feedback_rendered_view').text.strip()
        self.assertEquals(feedback, 'Hello world')
        self.assertEquals(delivery.find_element_by_css_selector('.gradeblock p .text-success').text.strip(),
                          'Passed')
        self.assertTrue('This is the active feedback' in delivery.text)

    def test_delivery_feedback_failed(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1.d1:ends(80)')
        self.testhelper.add_delivery(g1, {'b.py': ['print ', 'meh']})
        self.testhelper.add_feedback(g1, verdict={'grade': 'F', 'points': 5, 'is_passing_grade': False})

        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.show_deadline(deadline)
        delivery = self.get_deliveries(deadline)[0]

        self.assertEquals(delivery.find_element_by_css_selector('.gradeblock p .text-warning').text.strip(),
                          'Failed')


class TestManageSingleGroupNonElectronicDeadlinesAndDeliveries(DeadlineTestMixin, TestManageSingleGroupMixin,
                                                               SubjectAdminSeleniumTestCase):
    DELIVERY_TYPES = 'nonelectronic'

    def test_render_nonelectronic(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.testhelper.add_delivery(g1, {'a.py': ['print ', 'meh']})
        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.assertIn('Corrected deliveries', deadline.text)
        self.assertEquals(self.getDeliveryCount(deadline), 2)

    def test_nonelectronic_deliverymeta(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        self.testhelper.add_feedback(
            g1,
            verdict={'grade': 'C', 'points': 85, 'is_passing_grade': True},
            rendered_view="This is the feedback")
        self.browseToAndSelectAs('a1admin', g1)
        deadline = self.waitForDeadlineCount(1)[0]
        self.show_deadline(deadline)
        delivery = self.get_deliveries(deadline)[0]
        self.assertEquals(len(delivery.find_elements_by_css_selector('.no_feedback')), 0)
        feedback = delivery.find_element_by_css_selector('.feedback_rendered_view').text.strip()
        self.assertEquals(feedback, 'This is the feedback')
        self.assertEquals(
            'Passed',
            delivery.find_element_by_css_selector('.gradeblock p .text-success').text.strip())

        # Make sure we show what we should show, and hide what we should hide
        for cls in ('.gradeblock', '.activefeedbackblock'):
            self.assertEquals(len(delivery.find_elements_by_css_selector(cls)), 1)
        for cls in ('.timeofdeliveryblock', '.deliverymadebyblock', '.fileblock'):
            self.assertEquals(len(delivery.find_elements_by_css_selector(cls)), 0)


class TestManageSingleGroupDelete(TestManageSingleGroupMixin,
                                  SubjectAdminSeleniumTestCase,
                                  WaitForAlertMessageMixin):
    def test_delete(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        deletebutton = self.waitForAndFindElementByCssSelector('#single_group_delete_button button')
        sleep(1)
        deletebutton.click()

        window = self.waitForAndFindElementByCssSelector('.devilry_confirmdeletedialog')
        inputfield = window.find_element_by_css_selector('input[name=confirm_text]')
        deletebutton = window.find_element_by_css_selector('.devilry_deletebutton button')
        inputfield.send_keys('DELETE')
        self.waitForEnabled(deletebutton)
        deletebutton.click()
        self.waitForAlertMessage('success', 'Removed: student1')

        self.assertFalse(AssignmentGroup.objects.filter(id=g1.id).exists())
