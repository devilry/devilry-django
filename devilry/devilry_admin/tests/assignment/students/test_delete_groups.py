from __future__ import unicode_literals

import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy, timezone

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_admin.views.assignment.students import delete_groups
from devilry.devilry_admin.views.assignment.students.groupview_base import SelectedGroupsForm
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment


class TestDeleteGroupsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = delete_groups.DeleteGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Delete students',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Delete students',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_delete_with_content_warning_if_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'You have permission to delete students with deliveries and/or feedback, so be VERY CAREFUL '
            'before you click the delete button!',
            mockresponse.selector.one(
                '#devilry_admin_assignment_delete_groups_can_delete_content_warning').alltext_normalized)

    def test_no_delete_with_content_warning_if_not_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))
        self.assertFalse(
            mockresponse.selector.exists(
                '#devilry_admin_assignment_delete_groups_can_delete_content_warning'))

    def test_can_not_delete_with_content_message_if_subjectadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))
        self.assertEqual(
            'You do not have permission to delete students with deliveries and/or feedback, '
            'so those students are not available in the list below.',
            mockresponse.selector.one(
                '#devilry_admin_assignment_delete_groups_can_not_delete_content_message').alltext_normalized)

    def test_no_can_not_delete_with_content_message_if_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertFalse(
            mockresponse.selector.exists(
                '#devilry_admin_assignment_delete_groups_can_not_delete_content_message'))

    def test_groups_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            3,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_submit_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'Delete students',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_target_with_selected_items_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'Delete the following students:',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_exclude_groups_with_groupcomment_from_student_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_groupcomment_from_student_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_groupcomment_from_examiner_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_groupcomment_from_examiner_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_imageannotationcomment_from_student_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_imageannotationcomment_from_student_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_imageannotationcomment_from_examiner_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_imageannotationcomment_from_examiner_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_published_feedback_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_published_feedback_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_post_ok(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.assertEqual(2, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id)]}
            })
        self.assertEqual(0, AssignmentGroup.objects.count())

    def test_post_can_delete_groups_with_content_as_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        self.assertEqual(1, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup.id)]}
            })
        self.assertEqual(0, AssignmentGroup.objects.count())

    def test_post_can_not_delete_groups_with_content_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup.id)]}
            })
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            SelectedGroupsForm.invalid_students_selected_message,
            '')


class TestDeleteGroupsFromPreviousAssignmentConfirmView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = delete_groups.ConfirmView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def __set_grading_points_for_last_feedbackset(self, cached_data, points=0, publishing_datetime=None):
        if not publishing_datetime:
            publishing_datetime = timezone.now()
        cached_data.last_feedbackset.grading_published_datetime = publishing_datetime
        cached_data.last_feedbackset.grading_points = points
        cached_data.last_feedbackset.save()

    def __make_multiple_students_on_previous_assignment(self, assignment, num=2, failed=True):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        relatedstudent_list = []
        for i in range(num):
            relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
            assignment_group = mommy.make('core.AssignmentGroup', parentnode=assignment)
            mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assignment_group)
            if failed:
                self.__set_grading_points_for_last_feedbackset(cached_data=assignment_group.cached_data)
            else:
                self.__set_grading_points_for_last_feedbackset(cached_data=assignment_group.cached_data,
                                                               points=assignment.max_points)
            relatedstudent_list.append(relatedstudent)
        return relatedstudent_list

    def __make_multiple_students_on_current_assignment(self, relatedstudent_list, assignment):
        groups_list = []
        for relatedstudent in relatedstudent_list:
            assignment_group = mommy.make('core.AssignmentGroup', parentnode=assignment)
            mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assignment_group)
            groups_list.append(assignment_group)
        return groups_list

    def __get_selected_group_ids_to_be_removed(self, selector):
        # Helper method to get the id of all selected groups that will be posted to the view.
        ids_list = []
        for input_element in selector.list('input'):
            if input_element.get('name') == 'selected_items':
                ids_list.append(input_element.get('value'))
        return ids_list

    def test_get_no_students_on_the_assignment(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-delete-groups-confirm-no-groups'))
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_get_no_students_on_assignment_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        related_student = mommy.make('core.RelatedStudent', period=testperiod)
        group_assignment1 = mommy.make('core.AssignmentGroup', parentnode=past_assignment)
        group_assignment2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment1)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=group_assignment1.cached_data, points=past_assignment.max_points)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-delete-groups-confirm-no-groups'))
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_get_student_on_assignment_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        related_student = mommy.make('core.RelatedStudent', period=testperiod)
        group_assignment1 = mommy.make('core.AssignmentGroup', parentnode=past_assignment)
        group_assignment2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment1)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=group_assignment1.cached_data)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_get_multiple_students_on_assignment_only_one_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')

        # Assignment 1
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        assignment1_group1 = mommy.make('core.AssignmentGroup', parentnode=past_assignment)
        assignment1_group2 = mommy.make('core.AssignmentGroup', parentnode=past_assignment)

        # Assignment 2
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        assignment2_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        assignment2_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)

        # Relatedstudent 1 passed previous assignment
        related_student1 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser1')
        mommy.make('core.Candidate', relatedstudent=related_student1, assignment_group=assignment1_group1)
        mommy.make('core.Candidate', relatedstudent=related_student1, assignment_group=assignment2_group1)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=assignment1_group1.cached_data, points=past_assignment.max_points)

        # Relatedstudent 2 did not pass previous assignment
        related_student2 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser2')
        mommy.make('core.Candidate', relatedstudent=related_student2, assignment_group=assignment1_group2)
        mommy.make('core.Candidate', relatedstudent=related_student2, assignment_group=assignment2_group2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=assignment1_group2.cached_data)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))
        self.assertTrue(
            mockresponse.selector.one('.django-cradmin-listbuilder-itemvalue').alltext_normalized.startswith(related_student2.user.shortname))

    def test_get_project_groups_from_current_assignment_with_more_than_one_student_is_excluded(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        related_student1 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser1')
        related_student2 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser2')

        # Assignment 1
        assignment1_group1 = mommy.make('core.AssignmentGroup', parentnode=past_assignment)
        mommy.make('core.Candidate', relatedstudent=related_student1,assignment_group=assignment1_group1)
        self.__set_grading_points_for_last_feedbackset(cached_data=assignment1_group1.cached_data)

        # Assignment 2
        assignment2_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', relatedstudent=related_student1, assignment_group=assignment2_group1)
        mommy.make('core.Candidate', relatedstudent=related_student2, assignment_group=assignment2_group1)

        self.assertEqual(AssignmentGroup.objects.filter(parentnode=past_assignment).count(), 1)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))
        self.assertEqual(self.__get_selected_group_ids_to_be_removed(selector=mockresponse.selector), [])

    def test_get_correct_selected_items_single(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)

        # Make one failing students on assignment 1
        failed_relatedstudents = self.__make_multiple_students_on_previous_assignment(
            assignment=past_assignment, num=1)

        # Add students to current assignment
        groups_to_be_removed = self.__make_multiple_students_on_current_assignment(
            relatedstudent_list=failed_relatedstudents, assignment=current_assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        input_values = self.__get_selected_group_ids_to_be_removed(selector=mockresponse.selector)
        self.assertEqual(len(input_values), 1)
        self.assertIn(str(groups_to_be_removed[0].id), input_values)

    def test_get_correct_selected_items_multiple(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)

        # Make three failing students on assignment 1
        failed_relatedstudents = self.__make_multiple_students_on_previous_assignment(
            assignment=past_assignment, num=3)

        # Make three passing students on assignment 1
        passed_relatedstudents = self.__make_multiple_students_on_previous_assignment(
            assignment=past_assignment, num=3, failed=False)

        # Add students to current assignment
        groups_to_be_removed = self.__make_multiple_students_on_current_assignment(
            relatedstudent_list=failed_relatedstudents, assignment=current_assignment)
        groups_not_to_be_removed = self.__make_multiple_students_on_current_assignment(
            relatedstudent_list=passed_relatedstudents, assignment=current_assignment)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            }
        )
        input_values = self.__get_selected_group_ids_to_be_removed(selector=mockresponse.selector)
        self.assertEqual(len(input_values), 3)
        self.assertIn(str(groups_to_be_removed[0].id), input_values)
        self.assertIn(str(groups_to_be_removed[1].id), input_values)
        self.assertIn(str(groups_to_be_removed[2].id), input_values)

    def test_post_sanity(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        relatedstudent_list = self.__make_multiple_students_on_previous_assignment(assignment=past_assignment, num=10)
        groups_list = self.__make_multiple_students_on_current_assignment(
            relatedstudent_list=relatedstudent_list, assignment=current_assignment)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=past_assignment).count(), 10)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 10)
        self.mock_http302_postrequest(
            cradmin_role=current_assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
            viewkwargs={
                'from_assignment_id': past_assignment.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [str(group.id) for group in groups_list]
                }
            }
        )
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=past_assignment).count(), 10)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 0)

    def test_get_query_count(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        past_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        current_assignment = mommy.make('core.Assignment', parentnode=testperiod)
        relatedstudent_list = self.__make_multiple_students_on_previous_assignment(assignment=past_assignment, num=100)
        self.__make_multiple_students_on_current_assignment(
            relatedstudent_list=relatedstudent_list, assignment=current_assignment)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=past_assignment).count(), 100)
        self.assertEqual(AssignmentGroup.objects.filter(parentnode=current_assignment).count(), 100)

        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        with self.assertNumQueries(6):
            # 1 query to fetch the `from_assignment`
            # 1 query to fetch assignment groups to delete
            # 1 query to count for pagination
            # 1 exists query to check if there are any groups to be deleted
            # 2 query to fill the form, one for initial queryset and for items to submit
            self.mock_http200_getrequest_htmls(
                requestuser=requestuser,
                cradmin_role=current_assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole(devilryrole='subjectadmin'),
                viewkwargs={
                    'from_assignment_id': past_assignment.id
                }
            )
