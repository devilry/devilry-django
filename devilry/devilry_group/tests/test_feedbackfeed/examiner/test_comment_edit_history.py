from django.conf import settings
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import group_comment_history


class TestExaminerCommentEditHistoryView(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    General testing of what gets rendered to student view.
    """
    viewclass = group_comment_history.ExaminerGroupCommentHistoryView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_examiner(self, user):
        return baker.make('core.Examiner', relatedexaminer__user=user)

    def test_missing_comment_id_in_kwargs(self):
        testuser = baker.make('devilry_account.User')
        testgroup = baker.make('core.AssignmentGroup')
        self.__make_examiner(user=testuser)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser)

    def test_comment_does_not_exists_raises_404(self):
        testuser = baker.make('devilry_account.User', shortname='admin', fullname='Thor')
        testgroup = baker.make('core.AssignmentGroup')
        self.__make_examiner(user=testuser)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'group_comment_id': 1})

    def test_comment_no_history_no_history_items_rendered(self):
        testuser = baker.make('devilry_account.User', shortname='admin', fullname='Thor')
        testgroup = baker.make('core.AssignmentGroup')
        self.__make_examiner(user=testuser)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    def test_can_not_see_other_users_private_comments_history(self):
        testuser = baker.make('devilry_account.User', shortname='admin', fullname='Thor')
        testgroup = baker.make('core.AssignmentGroup')
        self.__make_examiner(user=testuser)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'group_comment_id': groupcomment.id})

    def test_can_see_private_history_entries_from_their_own_comments(self):
        testuser = baker.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = baker.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_examiner(user=testuser)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  feedback_set__group=testgroup)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   edited_by=groupcomment.user, _quantity=2)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   edited_by=groupcomment.user, _quantity=2)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE, edited_by=groupcomment.user, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 7)

    def test_can_not_see_private_history_entries_from_other_users(self):
        testuser = baker.make('devilry_account.User', shortname='admin', fullname='Thor')
        testperiod = baker.make_recipe('devilry.apps.core.period_active', admins=[testuser])
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=testperiod)
        self.__make_examiner(user=testuser)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   edited_by=groupcomment.user, _quantity=2)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   edited_by=groupcomment.user, _quantity=2)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE, edited_by=groupcomment.user, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 4)