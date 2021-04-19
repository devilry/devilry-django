import mock
from django.contrib import messages
from django.http import Http404
from django.template import defaultfilters
from django.test import TestCase, override_settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.student import group_comment_history
from devilry.devilry_group import devilry_group_baker_factories as group_baker


class TestStudentCommentEditHistoryView(TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    General testing of what gets rendered to student view.
    """
    viewclass = group_comment_history.StudentGroupCommentHistoryView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_comment_not_visible_to_everyone_raises_404(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=candidate.assignment_group,
                requestuser=candidate.relatedstudent.user,
                viewkwargs={'group_comment_id': groupcomment.id})

    def test_missing_comment_id_in_kwargs(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=candidate.assignment_group,
                requestuser=candidate.relatedstudent.user)

    def test_comment_does_not_exists_raises_404(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=candidate.assignment_group,
                requestuser=candidate.relatedstudent.user,
                viewkwargs={'group_comment_id': 1})

    def test_comment_no_history_no_history_items_rendered(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=False)
    def test_students_can_not_see_other_users_comment_edit_history(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_comment_no_history_no_history_items_rendered(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_comment_no_history_no_history_items_rendered(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.one('.devilry-comment-history-no-items').alltext_normalized,
                         'No comment-history available. This may be because you do not have access to see the '
                         'edit-history for this comment. If you think this is an error, please contact an '
                         'administrator.')

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_students_can_see_other_users_comment_edit_history(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertTrue(mockresponse.selector.exists('.devilry-comment-edit-history-item'))
        self.assertFalse(mockresponse.selector.exists('.devilry-comment-history-no-items'))

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_multiple_comment_edit_history_entries_rendered(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 3)

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_only_history_entries_visible_to_everyone_rendered(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE, _quantity=3)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS, _quantity=3)
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.count('.devilry-comment-edit-history-item'), 3)

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_history_entry_content(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        history_entry = baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                   pre_edit_text='Pre edit text')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.one('.devilry-comment-history-item__title').alltext_normalized,
                         '{}'.format(defaultfilters.date(timezone.localtime(history_entry.edited_datetime),
                                                         'DATETIME_FORMAT')))
        self.assertEqual(mockresponse.selector.one('.devilry-comment-history-item__description').alltext_normalized,
                         'Pre edit text')

    @override_settings(DEVILRY_COMMENT_STUDENTS_CAN_SEE_OTHER_USERS_COMMENT_HISTORY=True)
    def test_history_entries_render_order(self):
        candidate = baker.make('core.Candidate',
                               relatedstudent=baker.make('core.RelatedStudent'))
        groupcomment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=candidate.assignment_group,
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        history_entry1 = baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                                    visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                    edited_datetime=timezone.now() - timezone.timedelta(hours=10))
        history_entry2 = baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                                    visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                    edited_datetime=timezone.now() - timezone.timedelta(hours=14))
        history_entry3 = baker.make('devilry_group.GroupCommentEditHistory', group_comment=groupcomment,
                                    visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                    edited_datetime=timezone.now() - timezone.timedelta(hours=4))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=candidate.assignment_group,
            requestuser=candidate.relatedstudent.user,
            viewkwargs={'group_comment_id': groupcomment.id})
        self.assertEqual(mockresponse.selector.list('.devilry-comment-history-item__title')[0].alltext_normalized,
                         '{}'.format(defaultfilters.date(timezone.localtime(history_entry3.edited_datetime),
                                                         'DATETIME_FORMAT')))
        self.assertEqual(mockresponse.selector.list('.devilry-comment-history-item__title')[1].alltext_normalized,
                         '{}'.format(defaultfilters.date(timezone.localtime(history_entry1.edited_datetime),
                                                         'DATETIME_FORMAT')))
        self.assertEqual(mockresponse.selector.list('.devilry-comment-history-item__title')[2].alltext_normalized,
                         '{}'.format(defaultfilters.date(timezone.localtime(history_entry2.edited_datetime),
                                                         'DATETIME_FORMAT')))
