# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.contrib import messages
from django.conf import settings

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

    def test_link_urls_with_period_tags_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(6, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEquals(
            mock.call(appname='overview', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='add_tag', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='add_students', kwargs={'tag': 'a'}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[2]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='remove_students', kwargs={'tag': 'a'}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[3]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='add_examiners', kwargs={'tag': 'a'}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[4]
        )
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='remove_examiners', kwargs={'tag': 'a'}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[5]
        )

    def test_num_item_values_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod
        )
        self.assertEquals(mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'), 3)

    def test_item_value_buttons_text(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
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

    def test_query_count(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testuser
            )


class TestAddTags(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.AddTagsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_add_single_tag(self):
        testperiod = mommy.make('core.Period')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'tag_text': 'tag1',
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                    'is_hidden': False
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
                        'is_hidden': False
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
                        'is_hidden': False
                    }
                }
            )
        self.assertEquals(7, PeriodTag.objects.count())


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
        self.assertEquals('Add examiners to tag a',
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
        self.assertEquals('Remove examiners from tag a',
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
