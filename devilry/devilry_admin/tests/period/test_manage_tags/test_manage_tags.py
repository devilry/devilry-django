# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.contrib import messages
from django.conf import settings

from django_cradmin import cradmin_testhelpers

import mock
from model_mommy import mommy

from devilry.devilry_admin.views.period.manage_tags import manage_tags
from devilry.apps.core.models import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAddTags(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.AddTagsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_add_single_tags(self):
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
