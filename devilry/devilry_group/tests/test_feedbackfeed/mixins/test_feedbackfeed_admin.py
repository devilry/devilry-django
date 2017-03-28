# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock

from django import http
from django.conf import settings
from django.http import Http404
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.devilry_group.cradmin_instances import crinstance_admin
from devilry.devilry_group.tests.test_feedbackfeed.mixins import test_feedbackfeed_common


class TestFeedbackfeedAdminMixin(test_feedbackfeed_common.TestFeedbackFeedMixin):
    """
    Mixin testclass for admin feedbackfeed tests.

    Add tests for functionality and ui that all admin views share.
    """
    viewclass = None

    def test_get(self):
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=candidate.assignment_group,
                                                          requestuser=candidate.relatedstudent.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          candidate.assignment_group.assignment.get_path())

    def test_get_examiner_discuss_tab_buttons(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup)
        self.assertEquals(2, mockresponse.selector.count('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_event_delivery_passed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                grading_points=7)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-passed'))
        self.assertFalse(mockresponse.selector.exists('.devilry-core-grade-failed'))

    def test_get_feedbackfeed_event_delivery_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=10,
                                       passing_grade_min_points=5)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = group_mommy.feedbackset_first_attempt_published(
                group=testgroup,
                grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-core-grade-failed'))
        self.assertFalse(mockresponse.selector.exists('.devilry-core-grade-passed'))

    def test_get_feedbackfeed_periodadmin(self):
        period = mommy.make('core.Period')
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        admin = mommy.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=mommy.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)

        comment = mommy.make('devilry_group.GroupComment',
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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_comment_admin(self):
        admin = mommy.make('devilry_account.User', shortname='periodadmin', fullname='Thor the norse god')
        period = mommy.make_recipe('devilry.apps.core.period_active',
                                   admins=[admin],
                                   parentnode__admins=[mommy.make('devilry_account.User', shortname='subjectadmin')],
                                   parentnode__parentnode__admins=[mommy.make('devilry_account.User',
                                                                              shortname='nodeadmin')])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        admin = mommy.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user_role='admin',
                             user=admin,
                             feedback_set=testfeedbackset,
                             visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=comment.feedback_set.group)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment-admin'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_periodadmin_raise_404_semi_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment',
                                    parentnode=testperiod,
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_periodadmin_raise_404_fully_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment',
                                    parentnode=testperiod,
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_subjectadmin_can_see_student_name_semi_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate',
                               assignment_group=testgroup,
                               relatedstudent__user__shortname='teststudent')
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset)
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                                          cradmin_instance=mockrequest.cradmin_instance)

        self.assertFalse(mockresponse.selector.exists('.devilry-core-candidate-anonymous-name'))
        self.assertTrue(mockresponse.selector.exists('.devilry-user-verbose-inline'))
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_subjectadmin_raise_404_fully_anonymous(self):
        # Mocks the return value of the crinstance's get_devilry_role_for_requestuser to return the user role.
        # It's easier to read if we mock the return value rather than creating a
        # permission group(this crinstance-function with permission groups is tested separately for the instance)
        testassignment = mommy.make('core.Assignment',
                                    anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_instance.get_devilryrole_for_requestuser.return_value = 'subjectadmin'
        with self.assertRaisesMessage(http.Http404, ''):
            self.mock_getrequest(requestuser=testuser, cradmin_role=testgroup,
                                 cradmin_instance=mockrequest.cradmin_instance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_periodadmin_no_access(self):
        # Periodadmin does not have access to view when the user is not periodadmin for that period.
        period1 = mommy.make('core.Period')
        period2 = mommy.make('core.Period')
        admin = mommy.make(settings.AUTH_USER_MODEL)
        permissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                     permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     period=period2)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=permissiongroup.permissiongroup)

        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period1)

        mockrequest = mock.MagicMock()
        mockrequest.user = admin
        mockrequest.cradmin_role = testgroup
        crinstance = crinstance_admin.AdminCrInstance(request=mockrequest)

        with self.assertRaises(Http404):
            self.mock_getrequest(cradmin_role=testgroup, cradmin_instance=crinstance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_subjectadmin_no_access(self):
        # Subjectadmin does not have access to view when the user is not subjectadmin for that perdiod
        subject1 = mommy.make('core.Subject')
        subject2 = mommy.make('core.Subject')
        admin = mommy.make(settings.AUTH_USER_MODEL)
        permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                     permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     subject=subject2)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=permissiongroup.permissiongroup)

        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode=subject1)

        mockrequest = mock.MagicMock()
        mockrequest.user = admin
        mockrequest.cradmin_role = testgroup
        crinstance = crinstance_admin.AdminCrInstance(request=mockrequest)

        with self.assertRaises(Http404):
            self.mock_getrequest(cradmin_role=testgroup, cradmin_instance=crinstance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_feedbackfeed_download_visible_public_commentfiles_exist(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   user=candidate.relatedstudent.user,
                                   feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar'))

    def test_get_feedbackfeed_download_not_visible_private_commentfile_exist(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar'))

    def test_get_feedbackfeed_download_not_visible_part_of_grading_not_published(self):
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   feedback_set=testfeedbackset,
                                   user=examiner.relatedexaminer.user,
                                   user_role='examiner',
                                   part_of_grading=True)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            cradmin_instance=mock_cradmininstance,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-sidebar'))

    def test_get_num_queries(self):
        period = mommy.make('core.Period')
        admin = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=mommy.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)

        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   user=candidate.relatedstudent.user,
                   user_role='student',
                   feedback_set=testfeedbackset,
                   _quantity=20)
        mommy.make('devilry_group.GroupComment',
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
        self.assertEquals(1, group_models.FeedbackSet.objects.count())

    def test_get_num_queries_with_commentfiles(self):
        """
        NOTE: (works as it should)
        Checking that no more queries are executed even though the
        :func:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder.__get_feedbackset_queryset`
        duplicates comment_file query.
        """
        period = mommy.make('core.Period')
        admin = mommy.make(settings.AUTH_USER_MODEL, shortname='thor', fullname='Thor Thunder God')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin,
                   permissiongroup=mommy.make(
                           'devilry_account.PeriodPermissionGroup',
                           permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN,
                           period=period).permissiongroup)
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=period)
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(group=testgroup)
        mommy.make('core.Candidate', assignment_group=testgroup, _quantity=50)
        examiner = mommy.make('core.Examiner', assignmentgroup=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, _quantity=50)
        candidate = mommy.make('core.Candidate', assignment_group=testgroup)
        comment = mommy.make('devilry_group.GroupComment',
                             user=candidate.relatedstudent.user,
                             user_role='student',
                             feedback_set=testfeedbackset)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user=examiner.relatedexaminer.user,
                              user_role='examiner',
                              feedback_set=testfeedbackset)
        mommy.make('devilry_comment.CommentFile',
                   filename='test.py',
                   comment=comment,
                   _quantity=20)
        mommy.make('devilry_comment.CommentFile',
                   filename='test2.py',
                   comment=comment2,
                   _quantity=20)
        mock_cradmininstance = mock.MagicMock()
        mock_cradmininstance.get_devilryrole_for_requestuser.return_value = 'periodadmin'
        with self.assertNumQueries(21):
            self.mock_http200_getrequest_htmls(cradmin_role=testgroup,
                                               requestuser=admin,
                                               cradmin_instance=mock_cradmininstance)
        self.assertEquals(1, group_models.FeedbackSet.objects.count())