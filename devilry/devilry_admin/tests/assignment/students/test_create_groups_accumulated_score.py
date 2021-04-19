import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from cradmin_legacy import cradmin_testhelpers
from django.contrib.contenttypes.models import ContentType

from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.apps.core.models import AssignmentGroup, Candidate, Assignment
from devilry.devilry_admin.views.assignment.students.create_groups_accumulated_score import \
    PreviewRelatedstudentsListView, SelectAssignmentsView


class TestAccumulatedScoreSelectAssignmentsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = SelectAssignmentsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_assignments(self):
        test_assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_assignment
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue'))

    def test_no_assignments_on_same_period(self):
        test_period = baker.make('core.Period')
        test_assignment1 = baker.make('core.Assignment', parentnode=test_period)
        baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_assignment1
        )
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-listbuilder-itemvalue'))

    def test_assignment_info(self):
        current_assignment = baker.make('core.Assignment')
        baker.make('core.Assignment', long_name='Test Assignment', max_points=123,
                   parentnode=current_assignment.parentnode)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment
        )
        selector = mockresponse.selector
        self.assertEqual(
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Test Assignment')
        self.assertEqual(
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized,
            'Max points: 123 Grading plugin: Passed/failed')

    def test_assignments_multiple(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', long_name='Test Assignment 1', max_points=123,
                                      parentnode=current_assignment.parentnode)
        test_assignment2 = baker.make('core.Assignment', long_name='Test Assignment 2', max_points=123,
                                      parentnode=current_assignment.parentnode)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment
        )
        selector = mockresponse.selector
        assignment_names = [element.alltext_normalized for element in
                            selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(len(assignment_names), 2)
        self.assertIn(test_assignment1.long_name, assignment_names)
        self.assertIn(test_assignment2.long_name, assignment_names)

    def test_session_data_cleared(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', long_name='Test Assignment 1', max_points=123,
                                      parentnode=current_assignment.parentnode)
        test_assignment2 = baker.make('core.Assignment', long_name='Test Assignment 2', max_points=123,
                                      parentnode=current_assignment.parentnode)
        session = self.client.session
        session['selected_assignment_ids'] = [125, 312]
        session['from_select_assignment_view'] = ''
        session['points_threshold'] = 512
        session.save()
        self.assertEqual(len(list(self.client.session.keys())), 3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock=self.client.session)
        self.assertEqual(len(list(mockresponse.request.session.keys())), 0)

    def test_post_session_data_set(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', long_name='Test Assignment 1', max_points=123,
                                      parentnode=current_assignment.parentnode)
        test_assignment2 = baker.make('core.Assignment', long_name='Test Assignment 2', max_points=123,
                                      parentnode=current_assignment.parentnode)
        self.assertEqual(len(list(self.client.session.keys())), 0)
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            sessionmock=self.client.session,
            requestkwargs={
                'data': {
                    'selected_items': [test_assignment1.id, test_assignment2.id],
                    'points_threshold': 123
                }
            })
        self.assertEqual(len(list(mockresponse.request.session.keys())), 3)
        self.assertEqual(mockresponse.request.session['from_select_assignment_view'], '')
        self.assertEqual(mockresponse.request.session['points_threshold'], 123)
        self.assertIn(test_assignment1.id, mockresponse.request.session['selected_assignment_ids'])
        self.assertIn(test_assignment2.id, mockresponse.request.session['selected_assignment_ids'])

    def test_session_data_cleared_and_set_again(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', long_name='Test Assignment 1', max_points=123,
                                      parentnode=current_assignment.parentnode)
        test_assignment2 = baker.make('core.Assignment', long_name='Test Assignment 2', max_points=123,
                                      parentnode=current_assignment.parentnode)
        session = self.client.session
        session['selected_assignment_ids'] = [125, 312]
        session['from_select_assignment_view'] = ''
        session['points_threshold'] = 512
        session.save()

        self.assertEqual(len(list(self.client.session.keys())), 3)
        self.assertEqual(self.client.session['from_select_assignment_view'], '')
        self.assertEqual(self.client.session['points_threshold'], 512)
        self.assertIn(125, self.client.session['selected_assignment_ids'])
        self.assertIn(312, self.client.session['selected_assignment_ids'])

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            sessionmock=self.client.session,
            requestkwargs={
                'data': {
                    'selected_items': [test_assignment1.id, test_assignment2.id],
                    'points_threshold': 123
                }
            })

        self.assertEqual(len(list(mockresponse.request.session.keys())), 3)
        self.assertEqual(mockresponse.request.session['from_select_assignment_view'], '')
        self.assertEqual(mockresponse.request.session['points_threshold'], 123)
        self.assertIn(test_assignment1.id, mockresponse.request.session['selected_assignment_ids'])
        self.assertIn(test_assignment2.id, mockresponse.request.session['selected_assignment_ids'])

    def test_post_without_point_threshold(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', long_name='Test Assignment 1', max_points=123,
                                      parentnode=current_assignment.parentnode)
        test_assignment2 = baker.make('core.Assignment', long_name='Test Assignment 2', max_points=123,
                                      parentnode=current_assignment.parentnode)
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock=self.client.session,
            requestkwargs={
                'data': {
                    'selected_items': [test_assignment1.id, test_assignment2.id]
                }
            })
        self.assertEqual(len(list(self.client.session.keys())), 0)
        self.assertEqual(mockresponse.selector.one('#error_1_id_points_threshold').alltext_normalized,
                         'This field is required.')

    def test_post_without_selected_items(self):
        current_assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock=self.client.session,
            requestkwargs={
                'data': {
                    'selected_items': [],
                    'points_threshold': 123
                }
            })
        self.assertEqual(len(list(self.client.session.keys())), 0)


class TestPreviewRelatedstudentsListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = PreviewRelatedstudentsListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_from_select_assignment_view_not_in_session(self):
        test_assignment = baker.make('core.Assignment')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=test_assignment,
                sessionmock={
                    'selected_assignment_ids': [],
                    'points_threshold': 10
                })

    def test_points_threshold_not_in_session(self):
        test_assignment = baker.make('core.Assignment')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=test_assignment,
                sessionmock={
                    'selected_assignment_ids': [],
                    'from_select_assignment_view': ''
                })

    def test_selected_assignment_ids_not_in_session(self):
        test_assignment = baker.make('core.Assignment')
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=test_assignment,
                sessionmock={
                    'points_threshold': 123,
                    'from_select_assignment_view': ''
                })

    def test_ok(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                     long_name='Test Assignment 1')
        self.mock_http200_getrequest_htmls(
            cradmin_role=test_assignment,
            sessionmock={
                'points_threshold': 123,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment.id]
            })

    def test_selected_assignments_info_box(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 1')
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 123,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id]
            })
        self.assertEqual(
            mockresponse.selector.one('.devilry-accumulated-score-selected-assignments').alltext_normalized,
            '- Test Assignment 1 - Test Assignment 2')

    def test_total_score_for_selected_assignments_info_box(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 1', max_points=100)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 2', max_points=150)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 123,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-total-max-score').alltext_normalized,
            'Total max score of selected assignments: 250')

    def test_threshold_percentage_of_max_score_info_box(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 1', max_points=100)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 2', max_points=150)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 123,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-threshold-percentage-of-max-score').alltext_normalized,
            'Threshold percentage of max score: {:.2f} %'.format((123.0/250.0) * 100.0))

    def test_single_assignment_single_student_not_passed_added_students_count_info_box(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                     long_name='Test Assignment 1')
        relatedstudent = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 1,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-student-count').alltext_normalized,
            'Number of students that will be added to the assignment: 0 / 1')

    def test_single_assignment_single_student_passed_added_students_count_info_box(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                     long_name='Test Assignment 1')
        relatedstudent = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment, grading_points=1)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 1,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-student-count').alltext_normalized,
            'Number of students that will be added to the assignment: 1 / 1')

    def test_single_assignment_multiple_students_added_students_count_info_box_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                     long_name='Test Assignment 1')
        relatedstudent1 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        relatedstudent2 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        relatedstudent3 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 1,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-student-count').alltext_normalized,
            'Number of students that will be added to the assignment: 2 / 3')

    def test_multiple_assignment_multiple_students_added_students_count_info_box_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 1')
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode,
                                      long_name='Test Assignment 2')
        relatedstudent1 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        relatedstudent2 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        relatedstudent3 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment1, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment2, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment1, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment2, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment1, grading_points=1)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment2, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'points_threshold': 2,
                'from_select_assignment_view': '',
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id]
            })
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-accumulated-score-selected-assignments-student-count').alltext_normalized,
            'Number of students that will be added to the assignment: 2 / 3')

    def __make_published_feedbackset_for_relatedstudent(self, relatedstudent, assignment, grading_points=0):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_first_attempt_published(group=group, grading_points=grading_points)
        baker.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)

    def test_single_assignment_student_has_enough_points_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment, grading_points=25)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment.id],
                'points_threshold': 25,
                'from_select_assignment_view': ''
            })
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)

    def test_single_assignment_student_does_not_have_enough_points_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment, grading_points=20)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment.id],
                'points_threshold': 25,
                'from_select_assignment_view': ''
            })
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 0)

    def test_multiple_assignments_student_has_enough_points_across_assignment_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=25)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            })
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 1)

    def test_student_details(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User',
                                    user__shortname='testuser@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=30)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            })
        selector = mockresponse.selector
        self.assertEqual(
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Test User (testuser@example.com)')
        self.assertEqual(
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized,
            'Grading points total: 55')

    def test_student_already_on_assignment_is_excluded(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User 2',
                                    user__shortname='testuser2@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=50)
        group = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', relatedstudent=relatedstudent,
                   assignment_group=group)
        baker.make('devilry_group.FeedbackSet', group=group)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            })
        self.assertNotContains(mockresponse.response, relatedstudent.user.fullname)
        self.assertNotContains(mockresponse.response, relatedstudent.user.shortname)

    def test_student_already_on_assignment_is_excluded_with_qualifying_student(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User 1',
                                    user__shortname='testuser1@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=30)
        relatedstudent_on_current_assignment = baker.make('core.RelatedStudent',
                                                          period=current_assignment.parentnode,
                                                          user__fullname='Test User 2',
                                                          user__shortname='testuser2@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent_on_current_assignment, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent_on_current_assignment, assignment=test_assignment2, grading_points=50)
        group = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', relatedstudent=relatedstudent_on_current_assignment,
                   assignment_group=group)
        baker.make('devilry_group.FeedbackSet', group=group)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            })
        self.assertNotContains(mockresponse.response, relatedstudent_on_current_assignment.user.fullname)
        self.assertNotContains(mockresponse.response, relatedstudent_on_current_assignment.user.shortname)
        self.assertContains(mockresponse.response, relatedstudent.user.fullname)
        self.assertContains(mockresponse.response, relatedstudent.user.shortname)

    def test_post_success_message(self):
        current_assignment = baker.make('core.Assignment', long_name='Current Assignment')
        test_assignment = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User',
                                    user__shortname='testuser@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment, grading_points=25)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            messagesmock=messagesmock,
            sessionmock={
                'selected_assignment_ids': [test_assignment.id],
                'points_threshold': 25,
                'from_select_assignment_view': ''
            },
            requestkwargs={
                'data': {
                    'confirm': ''
                }})
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            '1 student(s) added to Current Assignment',
            '')

    def test_post_one_student_group_created(self):
        current_assignment = baker.make('core.Assignment', long_name='Current Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User',
                                    user__shortname='testuser@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=25)
        self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            },
            requestkwargs={
                'data': {
                    'confirm': ''
                }})
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 1)
        assignment_group = AssignmentGroup.objects.filter(parentnode=current_assignment).get()
        self.assertEqual(
            Candidate.objects.filter(assignment_group=assignment_group, relatedstudent=relatedstudent).count(),
            1)

    def test_post_multiple_students_multiple_groups_created(self):
        current_assignment = baker.make('core.Assignment', long_name='Current Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent1 = baker.make('core.RelatedStudent',
                                     period=current_assignment.parentnode,
                                     user__fullname='Test User1',
                                     user__shortname='testuser1@example.com')
        relatedstudent2 = baker.make('core.RelatedStudent',
                                     period=current_assignment.parentnode,
                                     user__fullname='Test User2',
                                     user__shortname='testuser2@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment2, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment2, grading_points=25)
        self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            },
            requestkwargs={
                'data': {
                    'confirm': ''
                }})
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 2)
        self.assertEqual(Candidate.objects.filter(
            relatedstudent=relatedstudent1, assignment_group__parentnode=current_assignment).count(), 1)
        self.assertEqual(Candidate.objects.filter(
            relatedstudent=relatedstudent2, assignment_group__parentnode=current_assignment).count(), 1)

    def test_post_student_already_on_assignment_is_excluded(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=current_assignment.parentnode,
                                    user__fullname='Test User 1',
                                    user__shortname='testuser1@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent, assignment=test_assignment2, grading_points=30)
        relatedstudent_on_current_assignment = baker.make('core.RelatedStudent',
                                                          period=current_assignment.parentnode,
                                                          user__fullname='Test User 2',
                                                          user__shortname='testuser2@example.com')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent_on_current_assignment, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent_on_current_assignment, assignment=test_assignment2, grading_points=50)
        group = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', relatedstudent=relatedstudent_on_current_assignment,
                   assignment_group=group)
        baker.make('devilry_group.FeedbackSet', group=group)
        self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            sessionmock={
                'selected_assignment_ids': [test_assignment1.id, test_assignment2.id],
                'points_threshold': 50,
                'from_select_assignment_view': ''
            },
            requestkwargs={
                'data': {
                    'confirm': ''
                }})
        self.assertEqual(
            Candidate.objects.filter(relatedstudent=relatedstudent_on_current_assignment,
                                     assignment_group__parentnode=current_assignment).count(),
            1
        )

    def test_get_query_count_sanity(self):
        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment3 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment4 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent1 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment2, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment3, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment4, grading_points=30)

        relatedstudent2 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment2, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment3, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment4, grading_points=30)

        relatedstudent3 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment2, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment3, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment4, grading_points=30)

        relatedstudent4 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment1, grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment2, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment3, grading_points=30)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment4, grading_points=30)
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        with self.assertNumQueries(5):
            self.mock_getrequest(
                requestuser=requestuser,
                cradmin_role=current_assignment,
                sessionmock={
                    'selected_assignment_ids': [test_assignment1.id, test_assignment2.id,
                                                test_assignment3.id, test_assignment4.id],
                    'points_threshold': 50,
                    'from_select_assignment_view': ''
                })

    def test_post_query_count_sanity(self):
        # Trigger ContentType caching so we do not get an extra lookup in the
        # assertNumQueries() statement below.
        ContentType.objects.get_for_model(Assignment)

        current_assignment = baker.make('core.Assignment')
        test_assignment1 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment2 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment3 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        test_assignment4 = baker.make('core.Assignment', parentnode=current_assignment.parentnode, max_points=50)
        relatedstudent1 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment2, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment3, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1, assignment=test_assignment4, grading_points=50)

        relatedstudent2 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment2, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment3, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2, assignment=test_assignment4, grading_points=50)

        relatedstudent3 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment2, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment3, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent3, assignment=test_assignment4, grading_points=50)

        relatedstudent4 = baker.make('core.RelatedStudent', period=current_assignment.parentnode)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment1, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment2, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment3, grading_points=50)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent4, assignment=test_assignment4, grading_points=50)
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        with self.assertNumQueries(9):
            self.mock_http302_postrequest(
                requestuser=requestuser,
                cradmin_role=current_assignment,
                sessionmock={
                    'selected_assignment_ids': [test_assignment1.id, test_assignment2.id,
                                                test_assignment3.id, test_assignment4.id],
                    'points_threshold': 50,
                    'from_select_assignment_view': ''
                },
                requestkwargs={
                    'data': {
                        'confirm': ''
                    }})
