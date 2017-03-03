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

    def test_query_count(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        with self.assertNumQueries(4):
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
