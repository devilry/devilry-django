from time import sleep
from selenium.common.exceptions import StaleElementReferenceException

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_subjectadmin.tests.base import SubjectAdminSeleniumTestCase
from devilry.devilry_subjectadmin.tests.base import WaitForAlertMessageMixin


class TestManageMultipleStudentsMixin(object):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1

    def browseToAndSelectAs(self, username, select_groups=[]):
        select_ids = ','.join([str(group.id) for group in select_groups])
        path = '/assignment/{0}/@@manage-students/@@select/{1}'.format(self.assignment.id,
                                                                       select_ids)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_multiplegroupsview')

    def create_group(self, groupspec):
        self.testhelper.add_to_path('uni;sub.p1.a1.{0}'.format(groupspec))
        groupname = groupspec.split('.')[0].split(':')[0]
        return getattr(self.testhelper, 'sub_p1_a1_{0}'.format(groupname))

    def find_element(self, cssselector):
        return self.selenium.find_element_by_css_selector('.devilry_subjectadmin_multiplegroupsview {0}'.format(cssselector))

    def find_elements(self, cssselector):
        return self.selenium.find_elements_by_css_selector('.devilry_subjectadmin_multiplegroupsview {0}'.format(cssselector))


class TestManageMultipleStudentsCreateProjectGroups(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        self.waitForCssSelector('.merge_groups_helpbox')
        button = self.find_element('.merge_groups_button .x-btn-inner')
        helpbox = self.find_element('.merge_groups_helpbox')
        # self.assertEquals(button.text.strip(), 'Create project group')
        self.waitFor(button, lambda b: b.text.strip() == 'Create project group')
        self.waitFor(helpbox, lambda h: h.text.strip().startswith('Multiple students on a single group is used'))

    def test_show_and_hide(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        self.waitForCssSelector('.merge_groups_helpbox')
        buttonEl = self.find_element('.merge_groups_button button')
        help = self.find_element('.merge_groups_helpbox')
        confirmContainer = self.find_element('.merge_groups_confirmcontainer')

        self.assertFalse(confirmContainer.is_displayed())
        self.waitForDisplayed(help)
        buttonEl.click()
        self.waitFor(help, lambda h: not h.is_displayed()) # Wait for help to be hidden
        self.waitFor(buttonEl, lambda b: not b.is_displayed()) # Wait for button to be hidden
        self.waitFor(confirmContainer, lambda c: c.is_displayed()) # Wait for confirm to be displayed

        cancelButtonEl = self.find_element('.merge_groups_cancel_button')
        cancelButtonEl.click()
        self.waitFor(confirmContainer, lambda c: not c.is_displayed()) # Wait for confirm to be hidden
        self.waitFor(help, lambda h: h.is_displayed()) # Wait for help to be displayed
        self.waitFor(buttonEl, lambda b: b.is_displayed()) # Wait for button to be displayed

    def test_create_project_group(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        buttonEl = self.find_element('.merge_groups_button button')
        confirmContainer = self.find_element('.merge_groups_confirmcontainer')
        sleep(1)
        buttonEl.click()
        self.waitFor(confirmContainer, lambda c: c.is_displayed()) # Wait for confirm to be displayed

        createButtonEl = self.find_element('.merge_groups_confirm_button')
        createButtonEl.click()
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.devilry_subjectadmin_singlegroupview')) == 1)
        sleep(1)
        self.waitFor(self.selenium, lambda s: AssignmentGroup.objects.filter(id=g2.id).count() == 0)
        g1 = self.testhelper.reload_from_db(g1)
        candidates = set([c.student.username for c in g1.candidates.all()])
        self.assertEquals(candidates, {'student1', 'student2'})


class TestManageMultipleStudentsTags(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        self.waitForCssSelector('#multi_set_tags_button')
        self.waitForCssSelector('#multi_add_tags_button')
        self.waitForCssSelector('#multi_clear_tags_button')
        self.assertTrue(self.find_element('#multi_tags_help_and_buttons_container').is_displayed())
        self.assertFalse(self.find_element('#multi_set_tags_panel').is_displayed())
        self.assertFalse(self.find_element('#multi_add_tags_panel').is_displayed())

    def _has_reloaded(self, ignored):
        # Since the #multi_tags_help_and_buttons_container is invisible on the
        # save, it will not become visible again until reloaded
        panels = self.find_elements('#multi_tags_help_and_buttons_container')
        if panels:
            try:
                return panels[0].is_displayed()
            except StaleElementReferenceException:
                pass
        else:
            return False

    def test_set_tags(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        set_tags_button = self.waitForAndFindElementByCssSelector('#multi_set_tags_button')
        self.waitForDisplayed(set_tags_button)
        self.find_element('#multi_set_tags_button button').click()

        panel = self.find_element('#multi_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        panel.find_element_by_css_selector('textarea').send_keys('a,b')
        savebutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitFor(savebutton, lambda b: b.is_enabled())
        savebutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            tags = set([t.tag for t in group.tags.all()])
            self.assertEquals(tags, {'a', 'b'})

    def test_set_tags_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        set_tags_button = self.waitForAndFindElementByCssSelector('#multi_set_tags_button')
        self.waitForDisplayed(set_tags_button)
        self.find_element('#multi_set_tags_button button').click()

        panel = self.find_element('#multi_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.choosetags_cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_tags_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

    def test_add_tags(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        add_tags_button = self.waitForAndFindElementByCssSelector('#multi_add_tags_button')
        self.waitForDisplayed(add_tags_button)
        self.find_element('#multi_add_tags_button button').click()

        panel = self.find_element('#multi_add_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        panel.find_element_by_css_selector('textarea').send_keys('a,b')
        savebutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitFor(savebutton, lambda b: b.is_enabled())
        savebutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            tags = set([t.tag for t in group.tags.all()])
            self.assertEquals(tags, {'a', 'b'})

    def test_add_tags_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        add_tags_button = self.waitForAndFindElementByCssSelector('#multi_add_tags_button')
        self.waitForDisplayed(add_tags_button)
        self.find_element('#multi_add_tags_button button').click()

        panel = self.find_element('#multi_add_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.choosetags_cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_tags_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

    def test_clear_tags(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        g1.tags.create(tag='a')
        g2.tags.create(tag='b')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        clear_tags_button = self.waitForAndFindElementByCssSelector('#multi_clear_tags_button')
        self.waitForDisplayed(clear_tags_button)
        self.find_element('#multi_clear_tags_button button').click()

        panel = self.find_element('#multi_clear_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        okbutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            self.assertEquals(group.tags.all().count(), 0)

    def test_clear_tags_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        g1.tags.create(tag='a')
        g2.tags.create(tag='b')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        clear_tags_button = self.waitForAndFindElementByCssSelector('#multi_clear_tags_button')
        self.waitForDisplayed(clear_tags_button)
        self.find_element('#multi_clear_tags_button button').click()

        panel = self.find_element('#multi_clear_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_tags_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())


class TestManageMultipleStudentsExaminers(TestManageMultipleStudentsMixin,
                                          SubjectAdminSeleniumTestCase,
                                          WaitForAlertMessageMixin):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForCssSelector('#multi_set_examiners_button')
        self.waitForCssSelector('#multi_add_examiners_button')
        self.waitForCssSelector('#multi_clear_examiners_button')
        help_and_buttons_container = self.waitForAndFindElementByCssSelector(
            '#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(help_and_buttons_container)
        self.assertFalse(self.find_element('#multi_set_examiners_panel').is_displayed())
        self.assertFalse(self.find_element('#multi_add_examiners_panel').is_displayed())

    def _has_reloaded(self, ignored):
        # Since the #multi_examiners_help_and_buttons_container is invisible on the
        # save, it will not become visible again until reloaded
        panels = self.find_elements('#multi_examiners_help_and_buttons_container')
        if panels:
            try:
                return panels[0].is_displayed()
            except StaleElementReferenceException:
                pass
        return False

    def _create_related_examiner(self, username, fullname=None):
        user = self.testhelper.create_user(username, fullname=fullname)
        self.assignment.parentnode.relatedexaminer_set.create(user=user)

    def _find_gridrows(self):
        return self.find_elements('.devilry_subjectadmin_selectexaminersgrid .x-grid-row')

    def _get_row_by_username(self, username):
        for row in self._find_gridrows():
            matches = row.find_elements_by_css_selector('.examiner_username_{username}'.format(username=username))
            if len(matches) > 0:
                return row

    def _click_rowchecker_by_username(self, username):
        self._get_row_by_username(username).find_element_by_css_selector('.x-grid-row-checker').click()

    #
    # SET
    #

    def test_set_examiners(self):
        self._create_related_examiner('newexaminer', fullname='New Examiner')
        self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        g2 = self.create_group('g2:candidate(student2):examiner(examiner2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_examiners_help_and_buttons_container'))
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_set_examiners_button'))
        self.find_element('#multi_set_examiners_button button').click()

        panel = self.find_element('#multi_set_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        self.waitForCssSelector('.examiner_username_newexaminer')
        self.waitForCssSelector('.examiner_username_newexaminer2')
        self._click_rowchecker_by_username('newexaminer')
        self._click_rowchecker_by_username('newexaminer2')
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            examiners = set([e.user.username for e in group.examiners.all()])
            self.assertEquals(examiners, set(['newexaminer', 'newexaminer2']))

    def test_set_examiners_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_set_examiners_button'))
        self.find_element('#multi_set_examiners_button button').click()

        panel = self.find_element('#multi_set_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_examiners_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

    #
    # RANDOM DISTRIBUTE
    #

    def _click_advanced_button(self, cssselector):
        multi_advanced_examiners_button = self.waitForAndFindElementByCssSelector('#multi_advanced_examiners_button')
        self.waitForDisplayed(multi_advanced_examiners_button)
        multi_advanced_examiners_button.click()
        self.waitForAndFindElementByCssSelector(cssselector).click()

    def _randomdist_examiners(self, *usernames):
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self._click_advanced_button('#multi_randomdistribute_examiners_button')

        panel = self.find_element('#multi_randomdistribute_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        self.waitForCssSelector('.examiner_username_newexaminer')
        self.waitForCssSelector('.examiner_username_newexaminer2')
        for username in usernames:
            self._click_rowchecker_by_username(username)
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()
        self.waitForAlertMessage('success', 'Examiners random distributed successfully')

    def test_random_distribute_examiners(self):
        self._create_related_examiner('newexaminer', fullname='New Examiner')
        self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        g2 = self.create_group('g2:candidate(student2):examiner(examiner2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self._randomdist_examiners('newexaminer', 'newexaminer2')

        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(g1.examiners.count(), 1)
        g2 = self.testhelper.reload_from_db(g2)
        self.assertEquals(g1.examiners.count(), 1)
        self.assertNotEquals(g1.examiners.all()[0], g2.examiners.all()[0])

    def _get_groups_by_examiner(self, assignment, username):
        return AssignmentGroup.objects.filter(parentnode=assignment,
                                              examiners__user__username=username)

    def test_random_distribute_examiners_more(self):
        self._create_related_examiner('newexaminer', fullname='New Examiner')
        self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        g3 = self.create_group('g3:candidate(student2)')
        self.create_group('ignored:candidate(ignoredstudent)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2, g3])
        self._randomdist_examiners('newexaminer', 'newexaminer2')

        newexaminer_groups = self._get_groups_by_examiner(g1.parentnode, 'newexaminer')
        newexaminer2_groups = self._get_groups_by_examiner(g1.parentnode, 'newexaminer2')
        self.assertTrue((newexaminer_groups.count() == 1 and newexaminer2_groups.count() == 2) or
                        (newexaminer_groups.count() == 2 and newexaminer2_groups.count() == 1))

    def test_random_distribute_examiners_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForCssSelector('#multi_advanced_examiners_button button')
        self._click_advanced_button('#multi_randomdistribute_examiners_button')

        panel = self.find_element('#multi_randomdistribute_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_examiners_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

    #
    # ADD
    #

    def test_add_examiners(self):
        self._create_related_examiner('newexaminer', fullname='New Examiner')
        self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        g2 = self.create_group('g2:candidate(student2):examiner(examiner2)')

        # Load the page and click the "Add examiners" button
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_add_examiners_button'))
        self.find_element('#multi_add_examiners_button button').click()

        # Select newexaminer and newexaminer2, and save
        panel = self.find_element('#multi_add_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        self.waitForCssSelector('.examiner_username_newexaminer')
        self.waitForCssSelector('.examiner_username_newexaminer2')
        self._click_rowchecker_by_username('newexaminer')
        self._click_rowchecker_by_username('newexaminer2')
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()

        # Check the results
        self.waitFor(self.selenium, self._has_reloaded)
        g1 = self.testhelper.reload_from_db(g1)
        self.assertEquals(set([e.user.username for e in g1.examiners.all()]),
                          set(['examiner1', 'newexaminer', 'newexaminer2']))
        g2 = self.testhelper.reload_from_db(g2)
        self.assertEquals(set([e.user.username for e in g2.examiners.all()]),
                          set(['examiner2', 'newexaminer', 'newexaminer2']))

    def test_add_examiners_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_add_examiners_button'))
        self.find_element('#multi_add_examiners_button button').click()

        panel = self.find_element('#multi_add_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_examiners_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

    #
    # CLEAR
    #

    def test_clear_examiners(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        g2 = self.create_group('g2:candidate(student2):examiner(examiner2)')

        # Load page and click "Clear examiners"
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_clear_examiners_button'))
        self.find_element('#multi_clear_examiners_button button').click()

        # Confirm clear
        panel = self.find_element('#multi_clear_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        okbutton.click()

        # Check results
        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            self.assertEquals(group.examiners.all().count(), 0)

    def test_clear_examiners_cancel(self):
        g1 = self.create_group('g1:candidate(student1):examiner(examiner1)')
        g2 = self.create_group('g2:candidate(student2):examiner(examiner2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_examiners_help_and_buttons_container')
        self.waitForDisplayed(self.waitForAndFindElementByCssSelector('#multi_clear_examiners_button'))
        self.find_element('#multi_clear_examiners_button button').click()

        panel = self.find_element('#multi_clear_examiners_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_examiners_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())

        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            self.assertEquals(group.examiners.all().count(), 1)


class TestManageMultiGroupDelete(TestManageMultipleStudentsMixin,
                                 SubjectAdminSeleniumTestCase,
                                 WaitForAlertMessageMixin):
    def test_delete(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        ignored = self.create_group('ignored:candidate(student3)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        deletebutton = self.waitForAndFindElementByCssSelector('#multi_group_delete_button button')
        self.waitForDisplayed(deletebutton)
        deletebutton.click()

        window = self.waitForAndFindElementByCssSelector('.devilry_confirmdeletedialog')
        inputfield = window.find_element_by_css_selector('input[name=confirm_text]')
        deletebutton = window.find_element_by_css_selector('.devilry_deletebutton button')
        inputfield.send_keys('DELETE')
        self.waitForEnabled(deletebutton)
        deletebutton.click()
        self.waitForAlertMessage('success', 'Removed: student1, student2')

        self.assertFalse(AssignmentGroup.objects.filter(id=g1.id).exists())
        self.assertFalse(AssignmentGroup.objects.filter(id=g2.id).exists())
        self.assertTrue(AssignmentGroup.objects.filter(id=ignored.id).exists())
