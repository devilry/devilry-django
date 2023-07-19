# -*- coding: utf-8 -*-


from django import test
from django.contrib import messages
from django.conf import settings
from django.http import Http404

from cradmin_legacy import cradmin_testhelpers

import mock
from model_bakery import baker

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.views.period.manage_tags import manage_tags
from devilry.apps.core.models import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodTagListbuilderView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.TagListBuilderListView

    def test_title(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                          'Tags on {}'.format(testperiod.parentnode))

    def test_static_link_urls(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(2, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='overview', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEqual(
            mock.call(appname='manage_tags', args=(), viewname='add_tag', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )

    def test_num_item_values_rendered(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 3)

    def test_item_value_all_buttons_text(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(baker.make('core.RelatedExaminer', period=testperiod))
        testperiodtag.relatedstudents.add(baker.make('core.RelatedStudent', period=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_add_students_a').alltext_normalized,
            'Add students'
        )
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_students_a').alltext_normalized,
            'Remove students'
        )
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_add_examiners_a').alltext_normalized,
            'Add examiners'
        )
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_examiners_a').alltext_normalized,
            'Remove examiners'
        )

    def test_related_students_rendered(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        relatedstudent1 = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__shortname='relatedstudent1')
        relatedstudent2 = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__shortname='relatedstudent2')
        testperiodtag.relatedstudents.add(relatedstudent1, relatedstudent2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-core-periodtag-relatedstudents'))
        self.assertEqual(mockresponse.selector.count('.devilry-core-periodtag-relatedstudent'), 2)
        self.assertEqual(mockresponse.selector.one('.devilry-core-periodtag-relatedstudents').alltext_normalized,
                          'Students: relatedstudent1 , relatedstudent2')

    def test_no_related_students_rendered(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-core-periodtag-relatedstudents'))
        self.assertEqual(mockresponse.selector.one('.devilry-core-periodtag-no-relatedstudents').alltext_normalized,
                          'NO STUDENTS')

    def test_related_examiners_rendered(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        relatedexaminer1 = baker.make('core.RelatedExaminer',
                                    period=testperiod,
                                    user__shortname='relatedexaminer1')
        relatedexaminer2 = baker.make('core.RelatedExaminer',
                                    period=testperiod,
                                    user__shortname='relatedexaminer2')
        testperiodtag.relatedexaminers.add(relatedexaminer1, relatedexaminer2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-core-periodtag-relatedexaminers'))
        self.assertEqual(mockresponse.selector.count('.devilry-core-periodtag-relatedexaminer'), 2)
        self.assertIn('Examiners: ',
                      mockresponse.selector.one('.devilry-core-periodtag-relatedexaminers').alltext_normalized)

    def test_no_related_examiners_rendered(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-core-periodtag-relatedexaminers'))
        self.assertEqual(mockresponse.selector.one('.devilry-core-periodtag-no-relatedexaminers').alltext_normalized,
                          'NO EXAMINERS')

    def test_edit_button_rendered_when_prefix_is_blank(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertContains(mockresponse.response, 'Edit')

    def test_edit_delete_button_not_rendered_on_imported_tag(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-deletebutton'))

    def test_hide_button_rendered_when_custom_tag_is_not_hidden(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', is_hidden=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-hide-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-show-button'))

    def test_show_button_rendered_when_custom_tag_is_hidden(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-show-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-hide-button'))

    def test_edit_button_not_rendered_when_prefix_is_not_blank(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertNotContains(mockresponse.response, 'Edit')

    def test_delete_button_rendered_when_prefix_is_blank(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-deletebutton'))
        self.assertContains(mockresponse.response, 'Delete')

    def test_delete_button_not_rendered_when_prefix_is_not_blank(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue-editdelete-deletebutton'))
        self.assertNotContains(mockresponse.response, 'Delete')

    def test_remove_examiners_not_rendered(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_manage_tags_remove_examiners_a'))
        self.assertNotContains(mockresponse.response, 'Remove examiners')

    def test_remove_examiners_rendered(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod)
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_examiners_a').alltext_normalized,
            'Remove examiners')

    def test_remove_students_not_rendered(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_manage_tags_remove_students_a'))
        self.assertNotContains(mockresponse.response, 'Remove students')

    def test_remove_students_rendered(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod)
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEqual(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_students_a').alltext_normalized,
            'Remove students')

    def test_filter_search_on_tag(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-tag1'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'tag2')

    def test_filter_search_on_tag_no_results(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-tag3'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 0)
        self.assertNotContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'tag2')

    def test_filter_search_on_student_user_shortname(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent1'))
        testperiodtag2.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent1'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'relatedstudent1')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'relatedstudent2')

    def test_filter_search_on_student_user_shortname_matches_both(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_a'))
        testperiodtag2.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 2)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'relatedstudent_a')
        self.assertContains(mockresponse.response, 'tag2')
        self.assertContains(mockresponse.response, 'relatedstudent_b')

    def test_filter_search_on_student_user_shortname_no_result(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_a'))
        testperiodtag2.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent_c'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 0)
        self.assertNotContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'relatedstudent_a')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'relatedstudent_b')

    def test_filter_search_on_examiner_user_shortname(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer1'))
        testperiodtag2.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer1'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'relatedexaminer1')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'relatedexaminer2')

    def test_filter_search_on_examiner_user_shortname_matches_both(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_a'))
        testperiodtag2.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 2)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'relatedexaminer_a')
        self.assertContains(mockresponse.response, 'tag2')
        self.assertContains(mockresponse.response, 'relatedexaminer_b')

    def test_filter_search_on_examiner_user_shortname_no_result(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_a'))
        testperiodtag2.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer_c'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 0)
        self.assertNotContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'relatedexaminer_a')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'relatedexaminer_b')

    def test_filter_radio_show_all_tags(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3')
        baker.make('core.PeriodTag', period=testperiod, prefix='b', tag='tag4')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 4)
        self.assertContains(mockresponse.response,'tag1')
        self.assertContains(mockresponse.response, 'tag2')
        self.assertContains(mockresponse.response, 'tag3 (imported)')
        self.assertContains(mockresponse.response, 'tag4 (imported)')

    def test_filter_radio_show_hidden_tags_only(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-hidden-tags-only'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)
        self.assertNotContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertContains(mockresponse.response, 'tag3 (imported)')

    def test_filter_radio_show_visible_tags_only(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        baker.make('core.PeriodTag', period=testperiod, prefix='b', tag='tag4', is_hidden=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-visible-tags-only'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 3)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'tag3')
        self.assertNotContains(mockresponse.response, 'tag3 (imported)')
        self.assertContains(mockresponse.response, 'tag4 (imported)')

    def test_filter_radio_show_custom_tags_only(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-custom-tags-only'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 2)
        self.assertContains(mockresponse.response, 'tag1')
        self.assertContains(mockresponse.response, 'tag2')
        self.assertNotContains(mockresponse.response, 'tag3')
        self.assertNotContains(mockresponse.response, 'tag3 (imported)')

    def test_filter_radio_show_imported_tags_only(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-imported-tags-only'
            }
        )
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)
        self.assertNotContains(mockresponse.response, 'tag1')
        self.assertNotContains(mockresponse.response, 'tag2')
        self.assertContains(mockresponse.response, 'tag3 (imported)')

    def test_query_count(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod)
        testperiodtag3 = baker.make('core.PeriodTag', period=testperiod)
        testperiodtag1.relatedstudents.add(baker.make('core.RelatedStudent', period=testperiod))
        testperiodtag2.relatedstudents.add(baker.make('core.RelatedStudent', period=testperiod))
        testperiodtag3.relatedstudents.add(baker.make('core.RelatedStudent', period=testperiod))
        testperiodtag1.relatedexaminers.add(baker.make('core.RelatedExaminer', period=testperiod))
        testperiodtag2.relatedexaminers.add(baker.make('core.RelatedExaminer', period=testperiod))
        testperiodtag3.relatedexaminers.add(baker.make('core.RelatedExaminer', period=testperiod))
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testuser
            )


class TestHideShowPeriodTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.HideShowPeriodTag

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_period_missing_tag_id_parameter_raises_404(self):
        testperiod = baker.make('core.Period')
        with self.assertRaisesMessage(Http404, 'Missing parameters.'):
            self.mock_getrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {}})

    def test_period_tag_does_not_exist(self):
        testperiod = baker.make('core.Period')
        with self.assertRaisesMessage(Http404, 'Tag does not exist.'):
            self.mock_getrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'tag_id': 1
                    }})

    def test_period_tag_is_hidden_toggled_true(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        self.mock_getrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_id': testperiodtag.id
                }})
        self.assertTrue(PeriodTag.objects.get(id=testperiodtag.id).is_hidden)

    def test_period_tag_is_hidden_toggled_false(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', is_hidden=True)
        self.mock_getrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_id': testperiodtag.id
                }})
        self.assertFalse(PeriodTag.objects.get(id=testperiodtag.id).is_hidden)


class TestAddTags(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.AddTagsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_empty_tag_raises_validation_error(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': ''
                }
            }
        )
        self.assertEqual(
            mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized,
            'This field is required.'
        )
        self.assertEqual(PeriodTag.objects.count(), 0)

    def test_only_spaces_raises_validation_error(self):
        testperiod = baker.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': '      '
                }
            }
        )
        self.assertEqual(
            mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized,
            'This field is required.'
        )
        self.assertEqual(PeriodTag.objects.count(), 0)

    def test_empty_tags_ignored(self):
        testperiod = baker.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': ' tag1, , ,tag4 '
                }
            }
        )
        self.assertEqual(PeriodTag.objects.count(), 2)
        period_tags = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', period_tags)
        self.assertIn('tag4', period_tags)

    def test_add_correct_format_with_whitespace(self):
        testperiod = baker.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': '        tag1,       tag2',
                }
            }
        )
        self.assertEqual(PeriodTag.objects.count(), 2)
        period_tags = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', period_tags)
        self.assertIn('tag2', period_tags)

    def test_add_correct_format_with_newline_and_whitespace(self):
        testperiod = baker.make('core.Period')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1,\ntag2,      tag3,tag4    ',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(PeriodTag.objects.count(), 4)
        tagslist = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', tagslist)
        self.assertIn('tag2', tagslist)
        self.assertIn('tag3', tagslist)
        self.assertIn('tag4', tagslist)

    def test_add_single_tag(self):
        testperiod = baker.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1',
                }
            }
        )
        self.assertEqual(1, PeriodTag.objects.count())

    def test_add_single_tag_another_tag_exists(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag2',
                }
            }
        )
        self.assertEqual(2, PeriodTag.objects.count())

    def test_add_single_tag_message(self):
        testperiod = baker.make('core.Period')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(1, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '1 tag(s) added', '')

    def test_add_multiple_tags_message(self):
        testperiod = baker.make('core.Period')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1, tag2',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(2, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '2 tag(s) added', '')

    def test_add_multiple_tags_other_tags_exist(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, tag='tag3')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag4, tag5, tag6',
                }
            },
        )
        self.assertEqual(6, PeriodTag.objects.count())

    def test_add_multiple_tags_one_tag_exists_message(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1, tag2',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(2, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '1 tag(s) added, 1 tag(s) already existed and were ignored.', '')

    def test_add_multiple_tags(self):
        testperiod = baker.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1, tag2, tag3',
                }
            }
        )
        self.assertEqual(3, PeriodTag.objects.count())

    def test_add_single_tag_already_exists(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(1, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR, 'The tag(s) you wanted to add already exists.', '')

    def test_add_all_tags_already_exists(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        baker.make('core.PeriodTag', period=testperiod, tag='tag3')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1, tag2, tag3',
                }
            },
            messagesmock=messagesmock
        )
        self.assertEqual(3, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR, 'The tag(s) you wanted to add already exists.', '')

    def test_get_query_count(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        with self.assertNumQueries(1):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testuser,
                requestkwargs={
                    'data': {
                        'tag_text': 'tag1, tag2, tag3, tag4, tag5, tag6, tag7',
                    }
                }
            )

    def test_post_query_count(self):
        testperiod = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        with self.assertNumQueries(5):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestuser=testuser,
                requestkwargs={
                    'data': {
                        'tag_text': 'tag1, tag2, tag3, tag4, tag5, tag6, tag7',
                    }
                }
            )
        self.assertEqual(7, PeriodTag.objects.count())


class TestEditTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.EditTagView

    def test_title(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        self.assertEqual(mockresponse.selector.one('.cradmin-legacy-page-header-inner > h1').alltext_normalized,
                          'Edit {}'.format(testperiodtag.displayname))

    def test_tag_with_prefix_raises_404(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='ab')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'pk': testperiodtag.id
                })

    def test_rename_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'tag': 'tag2'
                }
            }
        )
        with self.assertRaises(PeriodTag.DoesNotExist):
            PeriodTag.objects.get(tag='tag1')
        self.assertEqual(PeriodTag.objects.count(), 1)
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag2'))

    def test_rename_tag_to_existing_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        baker.make('core.PeriodTag', period=testperiod, tag='tag2')
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'tag': 'tag2'
                }
            },
            messagesmock=messagesmock
        )
        self.assertContains(mockresponse.response, 'tag2 already exists')
        self.assertEqual(PeriodTag.objects.count(), 2)
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag1'))
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag2'))

    def test_error_tag_contains_comma(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'tag': 'tag1,asd'
                }
            },
            messagesmock=messagesmock
        )
        self.assertContains(mockresponse.response, 'Tag contains a comma(,).')
        self.assertEqual(PeriodTag.objects.count(), 1)
        self.assertEqual(PeriodTag.objects.all()[0].tag, 'tag1')

    def test_error_empty_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='tag1')
        messagesmock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'tag': '  '
                }
            },
            messagesmock=messagesmock
        )
        self.assertContains(mockresponse.response, 'Tag cannot be empty.')
        self.assertEqual(PeriodTag.objects.count(), 1)
        self.assertEqual(PeriodTag.objects.all()[0].tag, 'tag1')


class TestDeleteTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.DeleteTagView

    def test_title(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        self.assertEqual(mockresponse.selector.one('.cradmin-legacy-page-header-inner > h1').alltext_normalized,
                          'Delete {}'.format(testperiodtag.displayname))

    def test_tag_with_prefix_raises_404(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='ab')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'pk': testperiodtag.id
                })

    def test_delete_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        with self.assertRaises(PeriodTag.DoesNotExist):
            PeriodTag.objects.get(period=testperiod, tag=testperiodtag.tag)
        self.assertEqual(PeriodTag.objects.count(), 1)


class MockAddRelatedExaminerToTagView(manage_tags.RelatedExaminerAddView):
    model = RelatedExaminer


class MockRemoveRelatedExaminerFromTagView(manage_tags.RelatedExaminerRemoveView):
    model = RelatedExaminer


class TestMultiSelectAddRelatedUserView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    This class is just for testing the rendered UI parts of the multiselect view using
    RelatedExaminer as model.

    The multiselect view for RelatedExaminers and RelatedStudents works the same way, and the
    querysets fetched are identical(only the model is different). No special cases related to the model
    is tested here such as POST.
    """
    viewclass = MockAddRelatedExaminerToTagView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_title(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual('Add examiner to a',
                          mockresponse.selector.one('title').alltext_normalized)

    def test_get_relatedusers(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1')
        baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user1')
        self.assertContains(mockresponse.response, 'shortname_user2')

    def test_only_users_on_period_are_listed(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        period1_tag = baker.make('core.PeriodTag', period=testperiod1, tag='a')
        period2_tag = baker.make('core.PeriodTag', period=testperiod2, tag='a')
        baker.make('core.RelatedExaminer', period=testperiod1, user__shortname='shortname_user_testperiod1')
        baker.make('core.RelatedExaminer', period=testperiod2, user__shortname='shortname_user_testperiod2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod1,
            viewkwargs={
                'tag_id': period1_tag.id
            }
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user_testperiod1')
        self.assertNotContains(mockresponse.response, 'shortname_user_testperiod2')

    def test_get_only_users_not_registered_on_periodtag_are_selectable(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1')
        baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2')
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user3')
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user1')
        self.assertContains(mockresponse.response, 'shortname_user2')
        self.assertNotContains(mockresponse.response, 'shortname_user3')


class TestMultiSelectRemoveRelatedUserView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    This class is just for testing the rendered UI parts of the multiselect view using
    RelatedExaminer as model.

    The multiselect view for RelatedExaminers and RelatedStudents works the same way, and the
    querysets fetched are identical(only the model is different). No special cases related to the model
    is tested here such as POST.
    """
    viewclass = MockRemoveRelatedExaminerFromTagView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_title(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual('Remove examiner from a',
                          mockresponse.selector.one('title').alltext_normalized)

    def test_get_relatedusers(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1'))
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user1')
        self.assertContains(mockresponse.response, 'shortname_user2')

    def test_only_users_on_period_are_listed(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod1, tag='a')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod2, tag='a')
        testrelatedexaminer1 = baker.make('core.RelatedExaminer',
                                          period=testperiod1,
                                          user__shortname='shortname_user_testperiod1')
        testrelatedexaminer2 = baker.make('core.RelatedExaminer',
                                          period=testperiod2,
                                          user__shortname='shortname_user_testperiod2')
        testperiodtag1.relatedexaminers.add(testrelatedexaminer1)
        testperiodtag2.relatedexaminers.add(testrelatedexaminer2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod1,
            viewkwargs={
                'tag_id': testperiodtag1.id
            }
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user_testperiod1')
        self.assertNotContains(mockresponse.response, 'shortname_user_testperiod2')

    def test_get_only_users_registered_on_periodtag_are_selectable(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1'))
        testperiodtag.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2'))
        baker.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user3')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            }
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        self.assertContains(mockresponse.response, 'shortname_user1')
        self.assertContains(mockresponse.response, 'shortname_user2')
        self.assertNotContains(mockresponse.response, 'shortname_user3')
