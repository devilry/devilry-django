# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.contrib import messages
from django.conf import settings
from django.http import Http404

from django_cradmin import cradmin_testhelpers

import mock
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.views.period.manage_tags import manage_tags
from devilry.apps.core.models import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodTagListbuilderView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.TagListBuilderListView

    def test_title(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          'Tags on {}'.format(testperiod.parentnode))

    def test_static_link_urls(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(2, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEquals(
            mock.call(appname='overview', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='add_tag', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )

    # def test_link_urls_with_period_tags_rendered(self):
    #     testperiod = mommy.make('core.Period')
    #     testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
    #     testperiodtag.relatedexaminers.add(mommy.make('core.RelatedExaminer', period=testperiod))
    #     testperiodtag.relatedstudents.add(mommy.make('core.RelatedStudent', period=testperiod))
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
    #     self.assertEquals(6, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
    #     self.assertEquals(
    #         mock.call(appname='overview', args=(), viewname='INDEX', kwargs={}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
    #     )
    #     self.assertEquals(
    #         mock.call(appname='manage_tags', args=(), viewname='add_tag', kwargs={}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
    #     )
    #     self.assertEquals(
    #         mock.call('edit', args=(testperiodtag.id,), kwargs={}),
    #         mockresponse.request.cradmin_app.reverse_appurl.call_args_list[3]
    #     )
    #     self.assertEquals(
    #         mock.call('delete', args=(testperiodtag.id,), kwargs={}),
    #         mockresponse.request.cradmin_app.reverse_appurl.call_args_list[4]
    #     )
    #     self.assertEquals(
    #         mock.call(appname='manage_tags', args=(), viewname='add_students', kwargs={'tag': 'a'}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[5]
    #     )
    #     self.assertEquals(
    #         mock.call(appname='manage_tags', args=(), viewname='add_examiners', kwargs={'tag': 'a'}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[6]
    #     )
    #     self.assertEquals(
    #         mock.call(appname='manage_tags', args=(), viewname='remove_students', kwargs={'tag': 'a'}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[7]
    #     )
    #     self.assertEquals(
    #         mock.call(appname='manage_tags', args=(), viewname='remove_examiners', kwargs={'tag': 'a'}),
    #         mockresponse.request.cradmin_instance.reverse_url.call_args_list[8]
    #     )

    def test_num_item_values_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 3)

    def test_item_value_all_buttons_text(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(mommy.make('core.RelatedExaminer', period=testperiod))
        testperiodtag.relatedstudents.add(mommy.make('core.RelatedStudent', period=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_add_students_a').alltext_normalized,
            'Add students'
        )
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_students_a').alltext_normalized,
            'Remove students'
        )
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_add_examiners_a').alltext_normalized,
            'Add examiners'
        )
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_examiners_a').alltext_normalized,
            'Remove examiners'
        )

    def test_related_students_rendered(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod)
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__shortname='relatedstudent1')
        relatedstudent2 = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__shortname='relatedstudent2')
        testperiodtag.relatedstudents.add(relatedstudent1, relatedstudent2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-core-periodtag-relatedstudents'))
        self.assertEquals(mockresponse.selector.count('.devilry-core-periodtag-relatedstudent'), 2)
        self.assertEquals(mockresponse.selector.one('.devilry-core-periodtag-relatedstudents').alltext_normalized,
                          'Students: relatedstudent1 , relatedstudent2')

    def test_no_related_students_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-core-periodtag-relatedstudents'))
        self.assertEquals(mockresponse.selector.one('.devilry-core-periodtag-no-relatedstudents').alltext_normalized,
                          'NO STUDENTS')

    def test_related_examiners_rendered(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod)
        relatedexaminer1 = mommy.make('core.RelatedExaminer',
                                    period=testperiod,
                                    user__shortname='relatedexaminer1')
        relatedexaminer2 = mommy.make('core.RelatedExaminer',
                                    period=testperiod,
                                    user__shortname='relatedexaminer2')
        testperiodtag.relatedexaminers.add(relatedexaminer1, relatedexaminer2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-core-periodtag-relatedexaminers'))
        self.assertEquals(mockresponse.selector.count('.devilry-core-periodtag-relatedexaminer'), 2)
        self.assertIn('Examiners: ',
                      mockresponse.selector.one('.devilry-core-periodtag-relatedexaminers').alltext_normalized)

    def test_no_related_examiners_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-core-periodtag-relatedexaminers'))
        self.assertEquals(mockresponse.selector.one('.devilry-core-periodtag-no-relatedexaminers').alltext_normalized,
                          'NO EXAMINERS')

    def test_edit_button_rendered_when_prefix_is_blank(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertIn('Edit', mockresponse.response.content)

    def test_edit_delete_button_not_rendered_on_imported_tag(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-deletebutton'))

    def test_hide_button_rendered_when_custom_tag_is_not_hidden(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', is_hidden=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-hide-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-show-button'))

    def test_show_button_rendered_when_custom_tag_is_hidden(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-show-button'))
        self.assertFalse(mockresponse.selector.exists('.devilry-admin-manage-tags-imported-tag-hide-button'))

    def test_edit_button_not_rendered_when_prefix_is_not_blank(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-editbutton'))
        self.assertNotIn('Edit', mockresponse.response.content)

    def test_delete_button_rendered_when_prefix_is_blank(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-deletebutton'))
        self.assertIn('Delete', mockresponse.response.content)

    def test_delete_button_not_rendered_when_prefix_is_not_blank(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue-editdelete-deletebutton'))
        self.assertNotIn('Delete', mockresponse.response.content)

    def test_remove_examiners_not_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_manage_tags_remove_examiners_a'))
        self.assertNotIn('Remove examiners', mockresponse.response.content)

    def test_remove_examiners_rendered(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod)
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_examiners_a').alltext_normalized,
            'Remove examiners')

    def test_remove_students_not_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_manage_tags_remove_students_a'))
        self.assertNotIn('Remove students', mockresponse.response.content)

    def test_remove_students_rendered(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod)
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEquals(
            mockresponse.selector.one('#devilry_admin_period_manage_tags_remove_students_a').alltext_normalized,
            'Remove students')

    def test_filter_search_on_tag(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-tag1'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)

    def test_filter_search_on_tag_no_results(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-tag3'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 0)
        self.assertNotIn('tag1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)

    def test_filter_search_on_student_user_shortname(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent1'))
        testperiodtag2.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent1'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('relatedstudent1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertNotIn('relatedstudent2', mockresponse.response.content)

    def test_filter_search_on_student_user_shortname_matches_both(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_a'))
        testperiodtag2.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 2)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('relatedstudent_a', mockresponse.response.content)
        self.assertIn('tag2', mockresponse.response.content)
        self.assertIn('relatedstudent_b', mockresponse.response.content)

    def test_filter_search_on_student_user_shortname_no_result(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_a'))
        testperiodtag2.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod, user__shortname='relatedstudent_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedstudent_c'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 0)
        self.assertNotIn('tag1', mockresponse.response.content)
        self.assertNotIn('relatedstudent_a', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertNotIn('relatedstudent_b', mockresponse.response.content)

    def test_filter_search_on_examiner_user_shortname(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer1'))
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer1'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('relatedexaminer1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertNotIn('relatedexaminer2', mockresponse.response.content)

    def test_filter_search_on_examiner_user_shortname_matches_both(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_a'))
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 2)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('relatedexaminer_a', mockresponse.response.content)
        self.assertIn('tag2', mockresponse.response.content)
        self.assertIn('relatedexaminer_b', mockresponse.response.content)

    def test_filter_search_on_examiner_user_shortname_no_result(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag1')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, prefix='tag2')
        testperiodtag1.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_a'))
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='relatedexaminer_b'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'search-relatedexaminer_c'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 0)
        self.assertNotIn('tag1', mockresponse.response.content)
        self.assertNotIn('relatedexaminer_a', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertNotIn('relatedexaminer_b', mockresponse.response.content)

    def test_filter_radio_show_all_tags(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3')
        mommy.make('core.PeriodTag', period=testperiod, prefix='b', tag='tag4')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 4)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('tag2', mockresponse.response.content)
        self.assertIn('tag3 (imported)', mockresponse.response.content)
        self.assertIn('tag4 (imported)', mockresponse.response.content)

    def test_filter_radio_show_hidden_tags_only(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-hidden-tags-only'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertNotIn('tag1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertIn('tag3 (imported)', mockresponse.response.content)

    def test_filter_radio_show_visible_tags_only(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mommy.make('core.PeriodTag', period=testperiod, prefix='b', tag='tag4', is_hidden=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-visible-tags-only'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 3)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('tag2', mockresponse.response.content)
        self.assertNotIn('tag3', mockresponse.response.content)
        self.assertNotIn('tag3 (imported)', mockresponse.response.content)
        self.assertIn('tag4 (imported)', mockresponse.response.content)

    def test_filter_radio_show_custom_tags_only(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-custom-tags-only'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 2)
        self.assertIn('tag1', mockresponse.response.content)
        self.assertIn('tag2', mockresponse.response.content)
        self.assertNotIn('tag3', mockresponse.response.content)
        self.assertNotIn('tag3 (imported)', mockresponse.response.content)

    def test_filter_radio_show_imported_tags_only(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='tag3', is_hidden=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'filters_string': 'is_hidden-show-imported-tags-only'
            }
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertNotIn('tag1', mockresponse.response.content)
        self.assertNotIn('tag2', mockresponse.response.content)
        self.assertIn('tag3 (imported)', mockresponse.response.content)

    def test_query_count(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag3 = mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag1.relatedstudents.add(mommy.make('core.RelatedStudent', period=testperiod))
        testperiodtag2.relatedstudents.add(mommy.make('core.RelatedStudent', period=testperiod))
        testperiodtag3.relatedstudents.add(mommy.make('core.RelatedStudent', period=testperiod))
        testperiodtag1.relatedexaminers.add(mommy.make('core.RelatedExaminer', period=testperiod))
        testperiodtag2.relatedexaminers.add(mommy.make('core.RelatedExaminer', period=testperiod))
        testperiodtag3.relatedexaminers.add(mommy.make('core.RelatedExaminer', period=testperiod))
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testuser
            )


class TestHideShowPeriodTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.HideShowPeriodTag

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_period_tag_empty_prefix_raises_404(self):
        testperiod = mommy.make('core.Period')
        with self.assertRaisesMessage(Http404, 'Empty prefix or tag.'):
            self.mock_getrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'prefix': '',
                        'tag': 'a'
                    }})

    def test_period_tag_empty_tag_raises_404(self):
        testperiod = mommy.make('core.Period')
        with self.assertRaisesMessage(Http404, 'Empty prefix or tag.'):
            self.mock_getrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'prefix': 'a',
                        'tag': ''
                    }})

    def test_period_tag_does_not_exist_raises_404(self):
        testperiod = mommy.make('core.Period')
        with self.assertRaisesMessage(Http404, 'Tag error.'):
            self.mock_getrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'prefix': 'a',
                        'tag': 'b'
                    }})

    def test_period_tag_is_hidden_false_becomes_true(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='b')
        self.mock_getrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'prefix': testperiodtag.prefix,
                    'tag': testperiodtag.tag
                }})
        self.assertTrue(PeriodTag.objects.get(id=testperiodtag.id).is_hidden)

    def test_period_tag_is_hidden_true_becomes_false(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='b', is_hidden=True)
        self.mock_getrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'prefix': testperiodtag.prefix,
                    'tag': testperiodtag.tag
                }})
        self.assertFalse(PeriodTag.objects.get(id=testperiodtag.id).is_hidden)


class TestAddTags(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.AddTagsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_empty_tag_raises_validation_error(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': ''
                }
            }
        )
        self.assertEquals(
            mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized,
            'This field is required.'
        )
        self.assertEquals(PeriodTag.objects.count(), 0)

    def test_only_spaces_raises_validation_error(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': '      '
                }
            }
        )
        self.assertEquals(
            mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized,
            'This field is required.'
        )
        self.assertEquals(PeriodTag.objects.count(), 0)

    def test_empty_tags_ignored(self):
        testperiod = mommy.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': ' tag1, , ,tag4 '
                }
            }
        )
        self.assertEquals(PeriodTag.objects.count(), 2)
        period_tags = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', period_tags)
        self.assertIn('tag4', period_tags)

    def test_add_correct_format_with_whitespace(self):
        testperiod = mommy.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': '        tag1,       tag2',
                }
            }
        )
        self.assertEquals(PeriodTag.objects.count(), 2)
        period_tags = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', period_tags)
        self.assertIn('tag2', period_tags)

    def test_add_correct_format_with_newline_and_whitespace(self):
        testperiod = mommy.make('core.Period')
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
        self.assertEquals(PeriodTag.objects.count(), 4)
        tagslist = [periodtag.tag for periodtag in PeriodTag.objects.all()]
        self.assertIn('tag1', tagslist)
        self.assertIn('tag2', tagslist)
        self.assertIn('tag3', tagslist)
        self.assertIn('tag4', tagslist)

    def test_add_single_tag(self):
        testperiod = mommy.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1',
                }
            }
        )
        self.assertEquals(1, PeriodTag.objects.count())

    def test_add_single_tag_another_tag_exists(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag2',
                }
            }
        )
        self.assertEquals(2, PeriodTag.objects.count())

    def test_add_single_tag_message(self):
        testperiod = mommy.make('core.Period')
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
        self.assertEquals(1, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '1 tag(s) added', '')

    def test_add_multiple_tags_message(self):
        testperiod = mommy.make('core.Period')
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
        self.assertEquals(2, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '2 tag(s) added', '')

    def test_add_multiple_tags_other_tags_exist(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag3')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag4, tag5, tag6',
                }
            },
        )
        self.assertEquals(6, PeriodTag.objects.count())

    def test_add_multiple_tags_one_tag_exists_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
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
        self.assertEquals(2, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS, '1 tag(s) added, 1 tag(s) already existed and were ignored.', '')

    def test_add_multiple_tags(self):
        testperiod = mommy.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1, tag2, tag3',
                }
            }
        )
        self.assertEquals(3, PeriodTag.objects.count())

    def test_add_single_tag_already_exists(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
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
        self.assertEquals(1, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR, 'The tag(s) you wanted to add already exists.', '')

    def test_add_all_tags_already_exists(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag3')
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
        self.assertEquals(3, PeriodTag.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR, 'The tag(s) you wanted to add already exists.', '')

    def test_get_query_count(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
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
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
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
        self.assertEquals(7, PeriodTag.objects.count())


class TestEditTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.EditTagView

    def test_title(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        self.assertEquals(mockresponse.selector.one('.django-cradmin-page-header-inner > h1').alltext_normalized,
                          'Edit {}'.format(testperiodtag.displayname))

    def test_tag_with_prefix_raises_404(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='ab')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'pk': testperiodtag.id
                })

    def test_rename_tag(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
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
        self.assertEquals(PeriodTag.objects.count(), 1)
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag2'))

    def test_rename_tag_to_existing_tag(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
        mommy.make('core.PeriodTag', period=testperiod, tag='tag2')
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
        self.assertIn('tag2 already exists', mockresponse.response.content)
        self.assertEquals(PeriodTag.objects.count(), 2)
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag1'))
        self.assertIsNotNone(PeriodTag.objects.get(tag='tag2'))

    def test_error_tag_contains_comma(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
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
        self.assertIn('Tag contains a comma(,).', mockresponse.response.content)
        self.assertEquals(PeriodTag.objects.count(), 1)
        self.assertEquals(PeriodTag.objects.all()[0].tag, 'tag1')

    def test_error_empty_tag(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='tag1')
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
        self.assertIn('Tag cannot be empty.', mockresponse.response.content)
        self.assertEquals(PeriodTag.objects.count(), 1)
        self.assertEquals(PeriodTag.objects.all()[0].tag, 'tag1')


class TestDeleteTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.DeleteTagView

    def test_title(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        self.assertEquals(mockresponse.selector.one('.django-cradmin-page-header-inner > h1').alltext_normalized,
                          'Delete {}'.format(testperiodtag.displayname))

    def test_tag_with_prefix_raises_404(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='ab')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'pk': testperiodtag.id
                })

    def test_delete_tag(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'pk': testperiodtag.id
            }
        )
        with self.assertRaises(PeriodTag.DoesNotExist):
            PeriodTag.objects.get(period=testperiod, tag=testperiodtag.tag)
        self.assertEquals(PeriodTag.objects.count(), 1)


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
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals('Add examiners to a',
                          mockresponse.selector.one('title').alltext_normalized)

    def test_get_relatedusers(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1')
        mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user1', mockresponse.response.content)
        self.assertIn('shortname_user2', mockresponse.response.content)

    def test_only_users_on_period_are_listed(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod1, tag='a')
        mommy.make('core.PeriodTag', period=testperiod2, tag='a')
        mommy.make('core.RelatedExaminer', period=testperiod1, user__shortname='shortname_user_testperiod1')
        mommy.make('core.RelatedExaminer', period=testperiod2, user__shortname='shortname_user_testperiod2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod1,
            viewkwargs={
                'tag': 'a'
            }
        )
        self.assertEquals(1, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user_testperiod1', mockresponse.response.content)
        self.assertNotIn('shortname_user_testperiod2', mockresponse.response.content)

    def test_get_only_users_not_registered_on_periodtag_are_selectable(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1')
        mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2')
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user3')
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user1', mockresponse.response.content)
        self.assertIn('shortname_user2', mockresponse.response.content)
        self.assertNotIn('shortname_user3', mockresponse.response.content)


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
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals('Remove examiners from a',
                          mockresponse.selector.one('title').alltext_normalized)

    def test_get_relatedusers(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1'))
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user1', mockresponse.response.content)
        self.assertIn('shortname_user2', mockresponse.response.content)

    def test_only_users_on_period_are_listed(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod1, tag='a')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod2, tag='a')
        testrelatedexaminer1 = mommy.make('core.RelatedExaminer',
                                          period=testperiod1,
                                          user__shortname='shortname_user_testperiod1')
        testrelatedexaminer2 = mommy.make('core.RelatedExaminer',
                                          period=testperiod2,
                                          user__shortname='shortname_user_testperiod2')
        testperiodtag1.relatedexaminers.add(testrelatedexaminer1)
        testperiodtag2.relatedexaminers.add(testrelatedexaminer2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod1,
            viewkwargs={
                'tag': testperiodtag1.tag
            }
        )
        self.assertEquals(1, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user_testperiod1', mockresponse.response.content)
        self.assertNotIn('shortname_user_testperiod2', mockresponse.response.content)

    def test_get_only_users_registered_on_periodtag_are_selectable(self):
        testperiod = mommy.make('core.Period')
        testperiodtag = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user1'))
        testperiodtag.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user2'))
        mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='shortname_user3')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': testperiodtag.tag
            }
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('shortname_user1', mockresponse.response.content)
        self.assertIn('shortname_user2', mockresponse.response.content)
        self.assertNotIn('shortname_user3', mockresponse.response.content)
