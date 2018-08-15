# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.core import mail
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_feedback_simple
from devilry.devilry_group import models as group_models
from devilry.project.common import settings


class TestBulkCreateFeedbackSimplePassedFailedPlugin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback_simple.SimpleGroupBulkFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_form_tags(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.one('.grade_input'))
        self.assertTrue(mockresponse.selector.one('.comment_text_input'))

    def test_get_grade_choices_passed_failed(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertTrue(mockresponse.selector.exists('select'))
        choices = [choice.alltext_normalized for choice in mockresponse.selector.list('option')]
        self.assertIn('', choices)
        self.assertIn('Passed', choices)
        self.assertIn('Failed', choices)

    def test_group_single_candidate_display_names(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate',
                   relatedstudent__user__fullname='Candidate')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertEquals('Candidate(candidate)',
                          mockresponse.selector.one('.devilry-user-verbose-inline-both').alltext_normalized)

    def test_group_three_candidates_display_names(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate1',
                   relatedstudent__user__fullname='Candidate1')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate2',
                   relatedstudent__user__fullname='Candidate2')
        mommy.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate3',
                   relatedstudent__user__fullname='Candidate3')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertEquals('Candidate1(candidate1) , Candidate2(candidate2) , Candidate3(candidate3)',
                          mockresponse.selector.one('.devilry-assignmentgroup-users').alltext_normalized)

    def test_group_anonymization_semi_single_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertEquals('Automatic anonymous ID missing',
                          mockresponse.selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_group_anonymization_semi_multiple_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        candidate_names = [elem.alltext_normalized
                           for elem in mockresponse.selector.list('.devilry-core-candidate-anonymous-name')]
        self.assertEquals(3, len(candidate_names))
        for name in candidate_names:
            self.assertEquals(name, 'Automatic anonymous ID missing')

    def test_group_anonymization_fully_single_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        self.assertEquals('Automatic anonymous ID missing',
                          mockresponse.selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_group_anonymization_fully_multiple_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=user,
            cradmin_role=testassignment
        )
        candidate_names = [elem.alltext_normalized
                           for elem in mockresponse.selector.list('.devilry-core-candidate-anonymous-name')]
        self.assertEquals(3, len(candidate_names))
        for name in candidate_names:
            self.assertEquals(name, 'Automatic anonymous ID missing')

    def test_post_comment_attributes(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): 'Passed',
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, group_comments.count())
        feedback_comment = group_comments[0]
        self.assertEquals(feedback_comment.part_of_grading, True)
        self.assertEquals(feedback_comment.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEquals(feedback_comment.user, user)
        self.assertEquals(feedback_comment.user_role, group_models.GroupComment.USER_ROLE_EXAMINER)
        self.assertEquals(feedback_comment.text, 'you passed')
        self.assertEquals(feedback_comment.comment_type, group_models.GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        self.assertIsNotNone(feedback_comment.published_datetime)
        self.assertTrue(feedback_comment.published_datetime < feedback_comment.feedback_set.grading_published_datetime)

    def test_post_without_grading_not_saved(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): '',
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.get(group_id=testgroup.id)
        group_comments = group_models.GroupComment.objects.all()
        self.assertIsNone(cached_data.last_published_feedbackset)
        self.assertEquals(0, group_comments.count())

    def test_post_bulk_feedback_single_candidate_with_comment_text(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): 'Passed',
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.get(group_id=testgroup.id)
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, group_comments.count())
        self.assertEquals('you passed', group_comments[0].text)
        self.assertEquals(cached_data.last_feedbackset, cached_data.last_published_feedbackset)
        self.assertEquals(cached_data.last_published_feedbackset.grading_points, testassignment.max_points)

    def test_post_bulk_feedback_three_candidates_with_comment_text(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup1)
        mommy.make('core.Candidate', assignment_group=testgroup2)
        mommy.make('core.Candidate', assignment_group=testgroup3)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup1.id): 'Passed',
                    'comment_text_{}'.format(testgroup1.id): 'you passed',
                    'grade_{}'.format(testgroup2.id): 'Failed',
                    'comment_text_{}'.format(testgroup2.id): 'you failed',
                    'grade_{}'.format(testgroup3.id): 'Passed',
                    'comment_text_{}'.format(testgroup3.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.all()
        cached_data_group1 = cached_data.get(group_id=testgroup1)
        cached_data_group2 = cached_data.get(group_id=testgroup2)
        cached_data_group3 = cached_data.get(group_id=testgroup3)
        group_comments = group_models.GroupComment.objects.all()
        group_comment_group1 = group_comments.get(feedback_set__group_id=cached_data_group1.group_id)
        group_comment_group2 = group_comments.get(feedback_set__group_id=cached_data_group2.group_id)
        group_comment_group3 = group_comments.get(feedback_set__group_id=cached_data_group3.group_id)
        self.assertEquals(3, cached_data.count())
        self.assertEquals(3, group_comments.count())

        self.assertEquals('you passed', group_comment_group1.text)
        self.assertEquals(testassignment.max_points, group_comment_group1.feedback_set.grading_points)

        self.assertEquals('you failed', group_comment_group2.text)
        self.assertEquals(0, group_comment_group2.feedback_set.grading_points)

        self.assertEquals('you passed', group_comment_group3.text)
        self.assertEquals(testassignment.max_points, group_comment_group3.feedback_set.grading_points)

    def test_mails_feedback_mails_sent(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        student1 = mommy.make('core.Candidate', assignment_group=testgroup1)
        student2 = mommy.make('core.Candidate', assignment_group=testgroup2)
        student3 = mommy.make('core.Candidate', assignment_group=testgroup3)
        mommy.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        mommy.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        mommy.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup1.id): 'Passed',
                    'comment_text_{}'.format(testgroup1.id): 'you passed',
                    'grade_{}'.format(testgroup2.id): 'Failed',
                    'comment_text_{}'.format(testgroup2.id): 'you failed',
                    'grade_{}'.format(testgroup3.id): 'Passed',
                    'comment_text_{}'.format(testgroup3.id): 'you passed'
                }
            })
        self.assertEqual(len(mail.outbox), 3)

    def test_get_query_count(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup1)
        mommy.make('core.Candidate', assignment_group=testgroup2)
        mommy.make('core.Candidate', assignment_group=testgroup3)
        mommy.make('core.Candidate', assignment_group=testgroup4)
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='exam', fullname='Examiner')
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=user)

        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(
                requestuser=user,
                cradmin_role=testassignment
            )

    def test_post_query_count(self):
        # 1 query for each FeedbackSet update, and 2 queries for each GroupComment created(also creates Comment).
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        student1 = mommy.make('core.Candidate', assignment_group=testgroup1)
        student2 = mommy.make('core.Candidate', assignment_group=testgroup2)
        student3 = mommy.make('core.Candidate', assignment_group=testgroup3)
        mommy.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        mommy.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        mommy.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        with self.assertNumQueries(32):
            self.mock_http302_postrequest(
                requestuser=user,
                cradmin_role=testassignment,
                requestkwargs={
                    'data': {
                        'grade_{}'.format(testgroup1.id): 'Passed',
                        'comment_text_{}'.format(testgroup1.id): 'you passed',
                        'grade_{}'.format(testgroup2.id): 'Failed',
                        'comment_text_{}'.format(testgroup2.id): 'you failed',
                        'grade_{}'.format(testgroup3.id): 'Passed',
                        'comment_text_{}'.format(testgroup3.id): 'you passed',
                    }
                })


class TestBulkCreateFeedbackSimplePointsPlugin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback_simple.SimpleGroupBulkFeedbackView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_post_comment_attributes(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            max_points=100,
            passing_grade_min_points=60
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): 100,
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, group_comments.count())
        feedback_comment = group_comments[0]
        self.assertEquals(feedback_comment.part_of_grading, True)
        self.assertEquals(feedback_comment.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEquals(feedback_comment.user, user)
        self.assertEquals(feedback_comment.user_role, group_models.GroupComment.USER_ROLE_EXAMINER)
        self.assertEquals(feedback_comment.text, 'you passed')
        self.assertEquals(feedback_comment.comment_type, group_models.GroupComment.COMMENT_TYPE_GROUPCOMMENT)
        self.assertIsNotNone(feedback_comment.published_datetime)
        self.assertTrue(feedback_comment.published_datetime < feedback_comment.feedback_set.grading_published_datetime)

    def test_post_without_grading_not_saved(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            max_points=100,
            passing_grade_min_points=60
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): '',
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.get(group_id=testgroup.id)
        group_comments = group_models.GroupComment.objects.all()
        self.assertIsNone(cached_data.last_published_feedbackset)
        self.assertEquals(0, group_comments.count())

    def test_post_bulk_feedback_single_candidate_with_comment_text(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            max_points=100,
            passing_grade_min_points=60
        )
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup.id): 60,
                    'comment_text_{}'.format(testgroup.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.get(group_id=testgroup.id)
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(1, group_comments.count())
        self.assertEquals('you passed', group_comments[0].text)
        self.assertEquals(cached_data.last_feedbackset, cached_data.last_published_feedbackset)
        self.assertEquals(cached_data.last_published_feedbackset.grading_points, 60)

    def test_post_bulk_feedback_three_candidates_with_comment_text(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            max_points=100,
            passing_grade_min_points=60
        )
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup1)
        mommy.make('core.Candidate', assignment_group=testgroup2)
        mommy.make('core.Candidate', assignment_group=testgroup3)
        user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=user)
        self.mock_http302_postrequest(
            requestuser=user,
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'grade_{}'.format(testgroup1.id): 90,
                    'comment_text_{}'.format(testgroup1.id): 'you passed',
                    'grade_{}'.format(testgroup2.id): 50,
                    'comment_text_{}'.format(testgroup2.id): 'you failed',
                    'grade_{}'.format(testgroup3.id): 90,
                    'comment_text_{}'.format(testgroup3.id): 'you passed'
                }
            })
        cached_data = AssignmentGroupCachedData.objects.all()
        cached_data_group1 = cached_data.get(group_id=testgroup1)
        cached_data_group2 = cached_data.get(group_id=testgroup2)
        cached_data_group3 = cached_data.get(group_id=testgroup3)
        group_comments = group_models.GroupComment.objects.all()
        group_comment_group1 = group_comments.get(feedback_set__group_id=cached_data_group1.group_id)
        group_comment_group2 = group_comments.get(feedback_set__group_id=cached_data_group2.group_id)
        group_comment_group3 = group_comments.get(feedback_set__group_id=cached_data_group3.group_id)
        self.assertEquals(3, cached_data.count())
        self.assertEquals(3, group_comments.count())

        self.assertEquals('you passed', group_comment_group1.text)
        self.assertEquals(90, group_comment_group1.feedback_set.grading_points)

        self.assertEquals('you failed', group_comment_group2.text)
        self.assertEquals(50, group_comment_group2.feedback_set.grading_points)

        self.assertEquals('you passed', group_comment_group3.text)
        self.assertEquals(90, group_comment_group3.feedback_set.grading_points)
