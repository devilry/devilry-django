# -*- coding: utf-8 -*-


import mock

from django import http
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group import models as group_models
from devilry.devilry_group.cradmin_instances import crinstance_admin
from devilry.devilry_group.tests.test_feedbackfeed.mixins import mixin_feedbackfeed_common


class MixinTestFeedbackfeedAdmin(mixin_feedbackfeed_common.MixinTestFeedbackFeed):
    """
    Mixin testclass for admin feedbackfeed tests.

    Add tests for functionality and ui that all admin views share.
    """
    viewclass = None

    def __mock_cradmin_instance(self):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = 'admin'
        return mockinstance

    def test_get(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                          candidate.assignment_group.assignment.get_path())

    def test_move_deadline_button_rendered_if_deadline_expired_and_feedbackset_is_not_graded(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        deadline_datetime = timezone.now() - timezone.timedelta(days=1)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_active'))
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup,
                                                                             deadline_datetime=deadline_datetime)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            cradmin_instance=self.__mock_cradmin_instance()
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-group-event__grade-move-deadline-button'))

    def test_move_deadline_button_not_rendered_if_deadline_expired_and_feedbackset_is_graded(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        deadline_datetime = timezone.now() - timezone.timedelta(days=1)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_active'))
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group=testgroup, deadline_datetime=deadline_datetime, grading_published_datetime=deadline_datetime)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            cradmin_instance=self.__mock_cradmin_instance()
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-event__grade-move-deadline-button'))

    def test_new_attempt_button_rendered_if_deadline_expired_and_feedbackset_is_graded(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        deadline_datetime = timezone.now() - timezone.timedelta(days=1)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_active'))
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group=testgroup, deadline_datetime=deadline_datetime, grading_published_datetime=deadline_datetime)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            cradmin_instance=self.__mock_cradmin_instance()
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-group-event__grade-last-new-attempt-button'))

    def test_new_attempt_button_not_rendered_if_deadline_expired_and_feedbackset_not_graded(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        deadline_datetime = timezone.now() - timezone.timedelta(days=1)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__parentnode=baker.make_recipe('devilry.apps.core.period_active'))
        test_feedbackset = group_baker.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=deadline_datetime)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            cradmin_instance=self.__mock_cradmin_instance()
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-event__grade-last-new-attempt-button'))

    def test_assignment_deadline_hard_expired_comment_form_rendered(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        deadline_datetime = timezone.now() - timezone.timedelta(days=1)
        test_feedbackset = baker.make('devilry_group.FeedbackSet',
                                      deadline_datetime=deadline_datetime,
                                      group__parentnode__deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD,
                                      group__parentnode__parentnode=baker.make_recipe(
                                          'devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=test_feedbackset.group,
            requestuser=testuser,
            cradmin_instance=self.__mock_cradmin_instance()
        )
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-form-wrapper'))
        self.assertFalse(mockresponse.selector.exists('.devilry-feedbackfeed-form-disabled'))

    def test_get_examiner_discuss_tab_buttons(self):
        testgroup = baker.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertEqual(2, mockresponse.selector.count('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_event_delivery_passed(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_baker.feedbackset_first_attempt_published(
                group=testgroup,
                grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))
        self.assertFalse(mockresponse.selector.exists('.devilry-core-grade-failed'))

    def test_get_feedbackfeed_event_delivery_failed(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = baker.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_baker.feedbackset_first_attempt_published(
                group=testgroup,
                grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))
        self.assertFalse(mockresponse.selector.exists('.devilry-core-grade-passed'))

    def test_get_feedbackfeed_periodadmin(self):
        period = baker.make('core.Period')
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        admin = baker.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=baker.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)

        comment = baker.make('devilry_group.GroupComment',
                             user_role='admin',
                             user=admin,
                             text='Hello, is it me you\'re looking for?',
                             feedback_set=testfeedbackset,
                             visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertEqual(
            'periodadmin',
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=period, user=admin))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_comment_admin(self):
        admin = baker.make('devilry_account.User', shortname='periodadmin', fullname='Thor the norse god')
        period = baker.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin],
                                   parentnode__admins=[baker.make('devilry_account.User', shortname='subjectadmin')],
                                   parentnode__parentnode__admins=[baker.make('devilry_account.User',
                                                                              shortname='nodeadmin')])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        admin = baker.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        comment = baker.make('devilry_group.GroupComment',
                             user_role='admin',
                             user=admin,
                             feedback_set=testfeedbackset,
                             visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_periodadmin_raise_404_semi_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment',
                                    parentnode=testperiod,
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_periodadmin_raise_404_fully_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment',
                                    parentnode=testperiod,
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_subjectadmin_can_see_student_name_semi_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testassignment = baker.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = baker.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user__shortname='teststudent')
        baker.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset)
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                                          cradmin_instance=mockrequest.cradmin_instance)

        self.assertFalse(mockresponse.selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertTrue(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_subjectadmin_raise_404_fully_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testassignment = baker.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_periodadmin_no_access(self):
        # Periodadmin does not have access to view when the user is not periodadmin for that period.
        period1 = baker.make('core.Period')
        period2 = baker.make('core.Period')
        admin = baker.make(settings.AUTH_USER_MODEL)
        permissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                     permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     period=period2)
        baker.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=permissiongroup.permissiongroup)

        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period1)

        mockrequest = mock.MagicMock()
        mockrequest.user = admin
        mockrequest.cradmin_role = testgroup
        crinstance = crinstance_admin.AdminCrInstance(request=mockrequest)

        with self.assertRaises(Http404):
            self.mock_getrequest(cradmin_role=testgroup, cradmin_instance=crinstance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_subjectadmin_no_access(self):
        # Subjectadmin does not have access to view when the user is not subjectadmin for that perdiod
        subject1 = baker.make('core.Subject')
        subject2 = baker.make('core.Subject')
        admin = baker.make(settings.AUTH_USER_MODEL)
        permissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                     permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     subject=subject2)
        baker.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=permissiongroup.permissiongroup)

        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode__parentnode=subject1)

        mockrequest = mock.MagicMock()
        mockrequest.user = admin
        mockrequest.cradmin_role = testgroup
        crinstance = crinstance_admin.AdminCrInstance(request=mockrequest)

        with self.assertRaises(Http404):
            self.mock_getrequest(cradmin_role=testgroup, cradmin_instance=crinstance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_download_visible_public_commentfiles_exist(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = baker.make('core.Candidate', assignment_group=testgroup)
        group_comment = baker.make('devilry_group.GroupComment',
                                   user=candidate.relatedstudent.user,
                                   feedback_set=testfeedbackset)
        baker.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertTrue(
            'Download:' in mockresponse.selector.one('.devilry-group-feedbackfeed-buttonbar').alltext_normalized)

    def test_get_feedbackfeed_download_not_visible_private_commentfile_exist(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        group_comment = baker.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        baker.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertFalse(
            'Download:' in mockresponse.selector.one('.devilry-group-feedbackfeed-buttonbar').alltext_normalized)

    def test_get_feedbackfeed_download_not_visible_part_of_grading_not_published(self):
        testassignment = baker.make('core.Assignment')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        group_comment = baker.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   user=examiner.relatedexaminer.user,
                                   user_role='examiner',
                                   part_of_grading=True)
        baker.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertFalse(
            'Download:' in mockresponse.selector.one('.devilry-group-feedbackfeed-buttonbar').alltext_normalized)

    def test_get_no_edit_link_for_other_users_comments(self):
        admin = baker.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = baker.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user_role='examiner',
                   feedback_set=feedbackset)
        baker.make('devilry_group.GroupComment',
                   user_role='student',
                   feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup, requestuser=admin)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-comment-edit-link'))
        self.assertFalse(mockresponse.selector.exists('.devilry-group-comment-edit-link__admin'))
        self.assertFalse(mockresponse.selector.exists('.devilry-group-comment-edit-link__student'))
        self.assertFalse(mockresponse.selector.exists('.devilry-group-comment-edit-link__examiner'))

    def test_get_edit_link(self):
        admin = baker.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = baker.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user=admin,
                   user_role='admin',
                   feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                                          requestuser=admin)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-comment-edit-link__admin'))
        self.assertTrue('Edit',
                        mockresponse.selector.one('.devilry-group-comment-edit-link__admin').alltext_normalized)

    def test_get_edit_link_url(self):
        admin = baker.make('devilry_account.User', shortname='periodadmin', fullname='Thor')
        period = baker.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        feedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=admin,
                                  user_role='admin',
                                  feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                                          requestuser=admin)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-comment-edit-link__admin'))
        self.assertEqual(mockresponse.selector.one('.devilry-group-comment-edit-link__admin').get('href'),
                         '/devilry_group/admin/{}/feedbackfeed/groupcomment-edit/{}'.format(
                             testgroup.id, groupcomment.id))

    def test_get_num_queries(self):
        period = baker.make('core.Period')
        admin = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        baker.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=baker.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)

        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        baker.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        baker.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertNumQueries(18):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=admin,
                                               cradmin_instance=mock_cradmininstance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        period = baker.make('core.Period')
        admin = baker.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        baker.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=baker.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=period)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        baker.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = baker.make('core.Examiner', assignmentgroup=testgroup)
        baker.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = baker.make('core.Candidate', assignment_group=testgroup)
        comment = baker.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=testfeedbackset)
        comment2 = baker.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        baker.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=20)
        baker.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=20)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertNumQueries(18):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=admin,
                                               cradmin_instance=mock_cradmininstance)
        self.assertEqual(1, group_models.FeedbackSet.objects.count())