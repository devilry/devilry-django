# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.http import Http404
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.views.examiner.feedbackfeed_examiner import ExaminerEditGradeView


class TestEditGradeView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = ExaminerEditGradeView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_raises_404_feedbackset_is_not_last_feedbackset(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_published(group=testgroup, deadline_datetime=timezone.now())
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                viewkwargs={
                    'pk': testfeedbackset.id
                })

    def test_raises_404_one_feedbackset_unpublished(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                viewkwargs={
                    'pk': testfeedbackset.id
                })

    def test_raises_404_last_feedbackset_is_not_last_published_feedbackset(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        unpublished_feedbackset = group_mommy.feedbackset_new_attempt_unpublished(group=testgroup, deadline_datetime=timezone.now())
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                viewkwargs={
                    'pk': unpublished_feedbackset.id
                })

    def test_points_plugin_help_text(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                                           max_points=100,
                                           passing_grade_min_points=40)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=70)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        self.assertEquals(mockresponse.selector.one('#hint_id_grading_points').alltext_normalized,
                          'Give a score between 0 to 100 where 40 is the minimum amount of points needed to pass.')

    def test_points_plugin_initial_is_current_grade(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                                           max_points=100)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=70)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        input_element = mockresponse.selector.one('#id_grading_points')
        self.assertEquals(int(input_element.get('max')), 100)
        self.assertEquals(int(input_element.get('value')), 70)

    def test_passed_failed_plugin_help_text(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        self.assertEquals(mockresponse.selector.one('#hint_id_grading_points').alltext_normalized,
                          'Check the box to give a passing grade')

    def test_passed_failed_choices(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        input_element = mockresponse.selector.list('option')
        self.assertEquals(input_element[0].get('value'), 'Passed')
        self.assertEquals(input_element[1].get('value'), 'Failed')

    def test_passed_failed_plugin_initial_failed_if_failed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        input_element = mockresponse.selector.list('option')
        self.assertIsNone(input_element[0].get('selected'))
        self.assertEquals(input_element[1].get('selected'), 'selected')

    def test_passed_failed_plugin_initial_passed_if_passed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            viewkwargs={
                'pk': testfeedbackset.id
            })
        input_element = mockresponse.selector.list('option')
        self.assertEquals(input_element[0].get('selected'), 'selected')
        self.assertIsNone(input_element[1].get('selected'))
