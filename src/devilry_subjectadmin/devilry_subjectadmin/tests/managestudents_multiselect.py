from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup

from .base import SubjectAdminSeleniumTestCase



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


class TestManageMultipleStudentsOverview(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.top_infobox')
        top_infobox = self.find_element('.top_infobox')
        self.assertEquals(top_infobox.text.strip(),
                          '2/2 groups selected. Hold down CMD to select more groups.')


class TestManageMultipleStudentsCreateProjectGroups(TestManageMultipleStudentsMixin, SubjectAdminSeleniumTestCase):
    def test_render(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('.merge_groups_button')
        self.waitForCssSelector('.merge_groups_helpbox')
        button = self.find_element('.merge_groups_button')
        help = self.find_element('.merge_groups_helpbox')
        self.assertEquals(button.text.strip(), 'Create project group')
        self.assertTrue(help.text.strip().startswith('Multiple students on a single group is used'))

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
        self.assertTrue(help.is_displayed())
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
        buttonEl.click()
        self.waitFor(confirmContainer, lambda c: c.is_displayed()) # Wait for confirm to be displayed

        createButtonEl = self.find_element('.merge_groups_confirm_button')
        createButtonEl.click()
        self.waitFor(self.selenium, lambda s: len(s.find_elements_by_css_selector('.devilry_subjectadmin_singlegroupview')) == 1)
        self.assertFalse(AssignmentGroup.objects.filter(id=g2.id).exists())
        g1 = self.testhelper.reload_from_db(g1)
        candidates = set([c.student.username for c in g1.candidates.all()])
        self.assertEquals(candidates, set(['student1', 'student2']))


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
            return panels[0].is_displayed()
        else:
            return False

    def test_set_tags(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        self.waitForCssSelector('#multi_set_tags_button')
        self.find_element('#multi_set_tags_button button').click()

        panel = self.find_element('#multi_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        panel.find_element_by_css_selector('input[type=text]').send_keys('a,b')
        savebutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitFor(savebutton, lambda b: b.is_enabled())
        savebutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            tags = set([t.tag for t in group.tags.all()])
            self.assertEquals(tags, set(['a', 'b']))

    def test_set_tags_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        self.waitForCssSelector('#multi_set_tags_button')
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
        self.waitForCssSelector('#multi_add_tags_button')
        self.find_element('#multi_add_tags_button button').click()

        panel = self.find_element('#multi_add_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        panel.find_element_by_css_selector('input[type=text]').send_keys('a,b')
        savebutton = panel.find_element_by_css_selector('.choosetags_savebutton button')
        self.waitFor(savebutton, lambda b: b.is_enabled())
        savebutton.click()

        self.waitFor(self.selenium, self._has_reloaded)
        for group in (g1, g2):
            group = self.testhelper.reload_from_db(group)
            tags = set([t.tag for t in group.tags.all()])
            self.assertEquals(tags, set(['a', 'b']))

    def test_add_tags_cancel(self):
        g1 = self.create_group('g1:candidate(student1)')
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', select_groups=[g1, g2])
        self.waitForCssSelector('#multi_tags_help_and_buttons_container')
        self.waitForCssSelector('#multi_add_tags_button')
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
        self.waitForCssSelector('#multi_clear_tags_button')
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
        self.waitForCssSelector('#multi_clear_tags_button')
        self.find_element('#multi_clear_tags_button button').click()

        panel = self.find_element('#multi_clear_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        cancelbutton = panel.find_element_by_css_selector('.cancelbutton button')
        cancelbutton.click()

        help_and_buttons = self.find_element('#multi_tags_help_and_buttons_container')
        self.waitFor(help_and_buttons, lambda h: h.is_displayed())
