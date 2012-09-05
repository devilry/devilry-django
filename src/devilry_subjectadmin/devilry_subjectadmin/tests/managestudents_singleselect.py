from selenium.common.exceptions import StaleElementReferenceException
from devilry.apps.core.testhelper import TestHelper

from .base import SubjectAdminSeleniumTestCase



class TestManageSingleGroupMixin(object):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.assignment = self.testhelper.sub_p1_a1


    def browseToAndSelectAs(self, username, select_group):
        path = '/assignment/{0}/@@manage-students/@@select/{1}'.format(self.assignment.id,
                                                                       select_group.id)
        self.loginTo(username, path)
        self.waitForCssSelector('.devilry_subjectadmin_singlegroupview')

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
        g2 = self.create_group('g2:candidate(student2)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.top_infobox')
        top_infobox = self.find_element('.top_infobox')
        self.assertTrue(top_infobox.text.strip().startswith('Hold down CMD to select more groups.'))



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

    def test_no_popbutton_on_single(self):
        g1 = self.create_group('g1:candidate(student1)')
        self.browseToAndSelectAs('a1admin', g1)
        self.waitForCssSelector('.studentsingroupgrid_meta_student1')
        self.assertEquals(len(self.find_elements('.studentsingroupgrid_pop')), 0)

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
        self.waitForCssSelector('.devilry_subjectadmin_multiplegroupsview')
        self.assertEquals(len(self.find_listofgroups_rows(selected_only=True)), 2)

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
        self.waitForCssSelector('.devilry_subjectadmin_manageexaminersonsingle a.edit_examiners_button')
        setbutton = self.find_element('a.edit_examiners_button')
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
            self._get_relatedexaminer_row_by_username(examiner).click()
        okbutton = panel.find_element_by_css_selector('.okbutton button')
        self.waitFor(okbutton, lambda b: b.is_enabled())
        okbutton.click()

        # Wait for reload
        self.waitFor(self.selenium, self._has_reloaded)

    def test_set(self):
        newexaminer = self._create_related_examiner('newexaminer', fullname='New Examiner')
        newexaminer2 = self._create_related_examiner('newexaminer2', fullname='New Examiner 2')
        ignoredexaminer = self._create_related_examiner('ignoredexaminer', fullname='Ignored examiner') # NOTE: Not selected, but we need to make sure that this does not just seem to work, when, in reality "all" examiners are selected
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
        self._set_examiners(g1, click_examiners=['examiner1', 'examiner2']) # Should deselect them both
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

    def _has_reloaded(self, ignored):
        # Since the #single_tags_help_and_buttons_container is invisible on the
        # save, it will not become visible again until reloaded
        panels = self.find_elements('#single_tags_help_and_buttons_container')
        if panels:
            try:
                return panels[0].is_displayed()
            except StaleElementReferenceException:
                pass
        return False

    def _click_edit_tags_button(self):
        self.waitForCssSelector('.devilry_subjectadmin_managetagsonsingle a.edit_tags_button')
        setbutton = self.find_element('a.edit_tags_button')
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
        self.waitFor(self.selenium, self._has_reloaded) # Wait for reload

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
        g1.tags.create(tag='a')
        g1.tags.create(tag='b')
        self.browseToAndSelectAs('a1admin', g1)
        self._click_edit_tags_button()
        panel = self.find_element('#single_set_tags_panel')
        self.waitFor(panel, lambda p: p.is_displayed())
        inputfield = panel.find_element_by_css_selector('textarea')
        self.assertEquals(inputfield.get_attribute('value'), 'a,b')

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
