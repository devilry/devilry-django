# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test

from django_cradmin import cradmin_testhelpers

from model_mommy import mommy

from devilry.devilry_admin.views.period.manage_tags import examiners
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core.models.relateduser import RelatedExaminerTag, RelatedExaminer


class TestAddTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.AddTagMultiSelectView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_post_wrong_tags_format_in_form_1(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': ',,tag1'
                }
            }
        )
        self.assertEquals(0, RelatedExaminerTag.objects.count())
        self.assertEquals('Tag text must be in comma separated format! Example: tag1, tag2, tag3',
                          mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized)

    def test_post_wrong_tags_format_in_form_same_tag_twice(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'tag1, tag1'
                }
            }
        )
        self.assertEquals(0, RelatedExaminerTag.objects.count())
        self.assertEquals('"tag1" occurs more than once in the form.',
                          mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized)

    def test_post_add_single_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id],
                    'tag_text': 'tag1'
                }
            }
        )
        self.assertEquals(3, RelatedExaminerTag.objects.count())

    def test_post_add_multiple_tags(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id],
                    'tag_text': 'tag1, tag2'
                }
            }
        )
        self.assertEquals(6, RelatedExaminerTag.objects.count())

    def test_post_add_examiner_has_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        testexaminer4 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner4')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer1, tag='tag1')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id, testexaminer4.id],
                    'tag_text': 'tag1'
                }
            }
        )
        self.assertEquals(4, RelatedExaminerTag.objects.count())

    def test_post_add_tag_examiner_has_multiple_tags(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer, tag='tag1')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer, tag='tag3')
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'tag1, tag2, tag3'
                }
            }
        )
        self.assertEquals(3, RelatedExaminerTag.objects.count())
        self.assertEquals(3, RelatedExaminer.objects.get(id=testexaminer.id).relatedexaminertag_set.count())
        tags_for_examiner = RelatedExaminerTag.objects\
            .filter(relatedexaminer__id=testexaminer.id)\
            .values_list('tag', flat=True)
        self.assertEquals(3, len(tags_for_examiner))
        self.assertIn('tag1', tags_for_examiner)
        self.assertIn('tag2', tags_for_examiner)
        self.assertIn('tag3', tags_for_examiner)

    def test_post_add_tag_examiner_has_multiple_tags_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer, tag='tag1')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer, tag='tag3')
        with self.assertNumQueries(4):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [testexaminer.id],
                        'tag_text': 'tag1, tag2, tag3'
                    }
                }
            )
        self.assertEquals(3, RelatedExaminerTag.objects.count())
        self.assertEquals(3, RelatedExaminer.objects.get(id=testexaminer.id).relatedexaminertag_set.count())
        tags_for_examiner = RelatedExaminerTag.objects\
            .filter(relatedexaminer__id=testexaminer.id)\
            .values_list('tag', flat=True)
        self.assertEquals(3, len(tags_for_examiner))
        self.assertIn('tag1', tags_for_examiner)
        self.assertIn('tag2', tags_for_examiner)
        self.assertIn('tag3', tags_for_examiner)

    def test_post_add_tag_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        testexaminer4 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner4')
        testexaminer5 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner5')
        testexaminer6 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner6')
        testexaminer7 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner7')
        testexaminer8 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner8')
        testexaminer9 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner9')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer1, tag='tag1')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer1, tag='tag2')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer2, tag='tag2')
        mommy.make('core.RelatedExaminerTag', relatedexaminer=testexaminer3, tag='tag3')
        with self.assertNumQueries(4):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [
                            testexaminer1.id,
                            testexaminer2.id,
                            testexaminer3.id,
                            testexaminer4.id,
                            testexaminer5.id,
                            testexaminer6.id,
                            testexaminer7.id,
                            testexaminer8.id,
                            testexaminer9.id],
                        'tag_text': 'tag1, tag2, tag3'
                    }
                }
            )
        self.assertEquals(27, RelatedExaminerTag.objects.count())


class TestRemoveTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.RemoveTagMultiselectView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_examiners_registered_with_tag(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertNotIn('examiner1', mockresponse.response.content)
        self.assertNotIn('examiner2', mockresponse.response.content)
        self.assertNotIn('examiner3', mockresponse.response.content)
        self.assertEquals(0, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_multiple_examiners_registered_with_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        testexaminer4 = mommy.make('core.RelatedExaminer', user__shortname='examiner4', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer4)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            },
        )
        self.assertEquals(4, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_only_examiners_with_tag_is_listed(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='b', relatedexaminer=testexaminer3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertIn('examiner1', mockresponse.response.content)
        self.assertIn('examiner2', mockresponse.response.content)
        self.assertNotIn('examiner3', mockresponse.response.content)

    def test_examiner_not_registered_with_tag(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', user__shortname='examiner76', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertNotIn('examiner76', mockresponse.response.content)

    def test_only_examiner_registered_with_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', user__shortname='examiner76', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertIn('examiner76', mockresponse.response.content)

    def test_does_not_render_examiners_with_tags_and_prefix(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        mommy.make('core.RelatedExaminerTag', prefix='prefix', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', prefix='prefix', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', prefix='prefix', tag='a', relatedexaminer=testexaminer3)
        self.assertEquals(3, RelatedExaminerTag.objects.count())
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertEquals(0, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        self.assertNotIn('examiner1', mockresponse.response.content)
        self.assertNotIn('examiner2', mockresponse.response.content)
        self.assertNotIn('examiner3', mockresponse.response.content)

    def test_post_delete_tag_for_student(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', user__shortname='examiner76', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        self.assertEquals(1, RelatedExaminerTag.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                }
            }
        )
        self.assertEquals(0, RelatedExaminerTag.objects.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer.id).relatedexaminertag_set.count())

    def test_post_delete_tag_only_for_selected_students(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        self.assertEquals(3, RelatedExaminerTag.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id],
                }
            }
        )
        self.assertEquals(1, RelatedExaminerTag.objects.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer1.id).relatedexaminertag_set.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer2.id).relatedexaminertag_set.count())
        self.assertEquals(1, RelatedExaminer.objects.get(id=testexaminer3.id).relatedexaminertag_set.count())

    def test_get_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        testexaminer4 = mommy.make('core.RelatedExaminer', user__shortname='examiner4', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer4)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'manage_tag': 'remove',
                    'tag': 'a'
                },
            )

    def test_post_delete_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        testexaminer4 = mommy.make('core.RelatedExaminer', user__shortname='examiner4', period=testperiod)
        testexaminer5 = mommy.make('core.RelatedExaminer', user__shortname='examiner5', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer4)
        mommy.make('core.RelatedExaminerTag', tag='b', relatedexaminer=testexaminer5)
        self.assertEquals(5, RelatedExaminerTag.objects.count())
        with self.assertNumQueries(4):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                viewkwargs={
                    'manage_tag': 'remove',
                    'tag': 'a'
                },
                requestkwargs={
                    'data': {
                        'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id, testexaminer4.id],
                    }
                }
            )
        self.assertEquals(1, RelatedExaminerTag.objects.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer1.id).relatedexaminertag_set.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer2.id).relatedexaminertag_set.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer3.id).relatedexaminertag_set.count())
        self.assertEquals(0, RelatedExaminer.objects.get(id=testexaminer4.id).relatedexaminertag_set.count())
        self.assertEquals(1, RelatedExaminer.objects.get(id=testexaminer5.id).relatedexaminertag_set.count())


class TestReplaceTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.ReplaceTagMultiSelectView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_examiners_registered_with_tag(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage_tag': 'remove',
                'tag': 'a'
            }
        )
        self.assertNotIn('examiner1', mockresponse.response.content)
        self.assertNotIn('examiner2', mockresponse.response.content)
        self.assertNotIn('examiner3', mockresponse.response.content)
        self.assertEquals(0, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_post_wrong_tags_format_in_form_1(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'tag1'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': ',,tag1'
                }
            }
        )
        self.assertEquals(0, RelatedExaminerTag.objects.count())
        self.assertEquals('Tag text must be in comma separated format! Example: tag1, tag2, tag3',
                          mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized)

    def test_post_wrong_tags_format_in_form_same_tag_twice(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'tag1'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'tag1, tag1'
                }
            }
        )
        self.assertEquals(0, RelatedExaminerTag.objects.count())
        self.assertEquals('"tag1" occurs more than once in the form.',
                          mockresponse.selector.one('#error_1_id_tag_text').alltext_normalized)

    def test_replace_tag_for_single_user(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'b'
                }
            }
        )
        self.assertEquals(1, RelatedExaminerTag.objects.count())
        self.assertNotEquals('a', RelatedExaminerTag.objects.all()[0].tag)
        self.assertEquals('b', RelatedExaminerTag.objects.all()[0].tag)

    def test_replace_tag_and_add_for_single_user(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'b, c, d'
                }
            }
        )
        tags = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer)
        all_tags_list = [tag.tag for tag in tags]
        self.assertEquals(3, tags.count())
        self.assertNotIn('a', all_tags_list)
        self.assertIn('b', all_tags_list)
        self.assertIn('c', all_tags_list)
        self.assertIn('d', all_tags_list)

    def test_replace_tag_and_add_for_single_user_already_has_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        mommy.make('core.RelatedExaminerTag', tag='c', relatedexaminer=testexaminer)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'b, c, d'
                }
            }
        )
        tags = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer)
        all_tags_list = [tag.tag for tag in tags]
        self.assertEquals(3, tags.count())
        self.assertNotIn('a', all_tags_list)
        self.assertIn('b', all_tags_list)
        self.assertIn('c', all_tags_list)
        self.assertIn('d', all_tags_list)

    def test_replace_tag_and_add_for_multiple_users_already_has_tag(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='c', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='d', relatedexaminer=testexaminer2)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id],
                    'tag_text': 'b, c, d'
                }
            }
        )
        tags_examiner1 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer1)
        tags_examiner2 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer2)
        tags_examiner3 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer3)
        examiner1_tags_list = [tag.tag for tag in tags_examiner1]
        examiner2_tags_list = [tag.tag for tag in tags_examiner2]
        examiner3_tags_list = [tag.tag for tag in tags_examiner3]
        self.assertEquals(3, tags_examiner1.count())
        self.assertEquals(3, tags_examiner2.count())
        self.assertEquals(3, tags_examiner3.count())
        self.assertNotIn('a', examiner1_tags_list)
        self.assertNotIn('a', examiner2_tags_list)
        self.assertNotIn('a', examiner3_tags_list)

        self.assertIn('b', examiner1_tags_list)
        self.assertIn('c', examiner1_tags_list)
        self.assertIn('d', examiner1_tags_list)

        self.assertIn('b', examiner2_tags_list)
        self.assertIn('c', examiner2_tags_list)
        self.assertIn('d', examiner2_tags_list)

        self.assertIn('b', examiner3_tags_list)
        self.assertIn('c', examiner3_tags_list)
        self.assertIn('d', examiner3_tags_list)

    def test_replace_tag_and_add_user_already_has_tag_to_replace_with(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='b', relatedexaminer=testexaminer1)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id],
                    'tag_text': 'b, c, d'
                }
            }
        )
        self.assertEquals(2, RelatedExaminerTag.objects.count())

    def test_replace_tag_and_add_user_already_has_tag_but_is_not_first(self):
        testperiod = mommy.make('core.Period')
        testexaminer = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer)
        mommy.make('core.RelatedExaminerTag', tag='b', relatedexaminer=testexaminer)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer.id],
                    'tag_text': 'c, b, d'
                }
            }
        )
        tags = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer)
        self.assertEquals(3, tags.count())
        tags_list = [tag.tag for tag in tags]
        self.assertNotIn('a', tags_list)
        self.assertIn('c', tags_list)
        self.assertIn('b', tags_list)
        self.assertIn('d', tags_list)

    def test_replace_tag_for_multiple_users(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'manage-tag': 'replace',
                'tag': 'a'
            },
            requestkwargs={
                'data': {
                    'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id],
                    'tag_text': 'b'
                }
            }
        )
        tags = RelatedExaminerTag.objects.all()
        self.assertEquals(3, tags.count())
        self.assertNotEquals('a', tags[0].tag)
        self.assertNotEquals('a', tags[1].tag)
        self.assertNotEquals('a', tags[2].tag)
        self.assertEquals('b', tags[0].tag)
        self.assertEquals('b', tags[1].tag)
        self.assertEquals('b', tags[2].tag)

    def test_get_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', user__shortname='examiner1', period=testperiod)
        testexaminer2 = mommy.make('core.RelatedExaminer', user__shortname='examiner2', period=testperiod)
        testexaminer3 = mommy.make('core.RelatedExaminer', user__shortname='examiner3', period=testperiod)
        testexaminer4 = mommy.make('core.RelatedExaminer', user__shortname='examiner4', period=testperiod)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer4)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'manage_tag': 'replace',
                    'tag': 'a'
                },
            )

    def test_post_replace_query_count(self):
        testperiod = mommy.make('core.Period')
        testexaminer1 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner1')
        testexaminer2 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner2')
        testexaminer3 = mommy.make('core.RelatedExaminer', period=testperiod, user__shortname='examiner3')
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer2)
        mommy.make('core.RelatedExaminerTag', tag='a', relatedexaminer=testexaminer3)
        mommy.make('core.RelatedExaminerTag', tag='c', relatedexaminer=testexaminer1)
        mommy.make('core.RelatedExaminerTag', tag='c', relatedexaminer=testexaminer2)
        with self.assertNumQueries(7):
            self.mock_http302_postrequest(
                cradmin_role=testperiod,
                viewkwargs={
                    'manage-tag': 'replace',
                    'tag': 'a'
                },
                requestkwargs={
                    'data': {
                        'selected_items': [testexaminer1.id, testexaminer2.id, testexaminer3.id],
                        'tag_text': 'b, c, d'
                    }
                }
            )
        tags_examiner1 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer1)
        tags_examiner2 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer2)
        tags_examiner3 = RelatedExaminerTag.objects.filter(relatedexaminer=testexaminer3)
        self.assertEquals(3, tags_examiner1.count())
        self.assertEquals(3, tags_examiner2.count())
        self.assertEquals(3, tags_examiner3.count())
