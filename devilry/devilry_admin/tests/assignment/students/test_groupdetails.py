from datetime import timedelta

import htmls
import mock
from django import test
from django.http import Http404
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories
from devilry.apps.core.models import Assignment, AssignmentGroup
from devilry.devilry_admin.views.assignment.students import groupdetails
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestGroupDetailsRenderable(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_name(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_semi_anonymous_is_not_anonymized(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_name_fully_anonymous_is_not_anonymized(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_examiners(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_semi_anonymous(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_examiners_fully_anonymous(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__fullname='Test User',
                   relatedexaminer__user__shortname='testuser@example.com')
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.devilry-cradmin-groupitemvalue-examiners-names').alltext_normalized)

    def test_grade_students_can_see_points_false(self):
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group__parentnode__students_can_see_points=False,
            grading_points=1)
        testgroup = AssignmentGroup.objects.first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grade_students_can_see_points_true(self):
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group__parentnode__students_can_see_points=True,
            grading_points=1)
        testgroup = AssignmentGroup.objects.first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(
            value=testgroup, assignment=testgroup.assignment).render())
        self.assertEqual(
            'Grade: passed (1/1)',
            selector.one('.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_status_is_corrected(self):
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            grading_points=1)
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(value=testgroup,
                                                               assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_status_is_waiting_for_feedback(self):
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_feedback_count().first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(value=testgroup,
                                                               assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for feedback',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_status_is_waiting_for_deliveries(self):
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                first_deadline=timezone.now() + timedelta(days=2)))
        testgroup = AssignmentGroup.objects.annotate_with_is_waiting_for_deliveries_count().first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(value=testgroup,
                                                               assignment=testgroup.assignment).render())
        self.assertEqual(
            'Status: waiting for deliveries',
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_not_available_unless_corrected(self):
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished()
        testgroup = AssignmentGroup.objects.annotate_with_is_corrected_count().first()
        selector = htmls.S(groupdetails.GroupDetailsRenderable(value=testgroup,
                                                               assignment=testgroup.assignment).render())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_grade_comment_summary_is_available(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        baker.make('core.AssignmentGroup')
        testgroup = AssignmentGroup.objects.first()

        selector = htmls.S(groupdetails.GroupDetailsRenderable(value=testgroup,
                                                               assignment=testgroup.assignment).render())
        self.assertTrue(selector.exists('.devilry-cradmin-groupitemvalue-comments'))
        self.assertEqual(
            '0 comments from student. 0 files from student. 0 comments from examiner.',
            selector.one('.devilry-cradmin-groupitemvalue-comments').alltext_normalized)


class TestGroupDetailsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = groupdetails.GroupDetailsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertIn(
            'Test User',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertEqual(
            'Test User',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_links(self):
        testgroup = baker.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertEqual(2, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='studentoverview', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEqual(
            mock.call(appname='split_group', args=(), viewname='INDEX', kwargs={'pk': testgroup.id}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )

    def test_title_multiple_candidates(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='UserB')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               shortname='usera')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='UserC')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertIn(
            'usera, UserB, UserC',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1_multiple_candidates(self):
        testgroup = baker.make('core.AssignmentGroup')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='UserB')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               shortname='usera')
        devilry_core_baker_factories.candidate(group=testgroup,
                                               fullname='UserC')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertEqual(
            'usera, UserB, UserC',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_404_fully_anonymous_subjectadmin(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                viewkwargs={'pk': testgroup.id})

    def test_not_404_fully_anonymous_departmentadmin(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_getrequest(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id})
