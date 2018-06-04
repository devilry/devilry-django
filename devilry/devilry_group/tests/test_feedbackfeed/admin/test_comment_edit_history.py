from django.conf import settings
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.admin import group_comment_history


class TestAdminCommentEditHistoryView(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    General testing of what gets rendered to student view.
    """
    viewclass = group_comment_history.AdminGroupCommentHistoryView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_admin_comment(self, feedback_set, user=None):
        if not user:
            user = mommy.make(settings.AUTH_USER_MODEL)
        return mommy.make('devilry_group.GroupComment',
                          text='Test',
                          user=user,
                          user_role=group_models.GroupComment.USER_ROLE_ADMIN,
                          published_datetime=timezone.now(),
                          feedback_set=feedback_set)

    def __make_user_admin(self, user, assignment, permissiongroup_type='period'):
        if permissiongroup_type == 'period':
            permissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                         period=assignment.period)
        else:
            permissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                         period=assignment.period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=user,
                   permissiongroup=permissiongroup.permissiongroup)

    def test_missing_comment_id_in_kwargs(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser)

    def test_comment_does_not_exists_raises_404(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'group_comment_id': 1})

    def test_comment_no_history_no_history_items_rendered(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    def test_admin_can_not_see_other_users_private_comments_history(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'group_comment_id': groupcomment.id})

    def test_admin_can_see_private_history_entries_from_their_own_comments(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  user=testuser,
                                  feedback_set__group=testgroup)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   edited_by=groupcomment.user, _quantity=2)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   edited_by=groupcomment.user, _quantity=2)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE, edited_by=groupcomment.user, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 7)

    def test_admin_can_not_see_private_history_entries_from_other_users(self):
        testuser = mommy.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = mommy.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = mommy.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_user_admin(user=testuser, assignment=testgroup.parentnode)
        groupcomment = mommy.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   edited_by=groupcomment.user, _quantity=2)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   edited_by=groupcomment.user, _quantity=2)
        mommy.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE, edited_by=groupcomment.user, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 4)
