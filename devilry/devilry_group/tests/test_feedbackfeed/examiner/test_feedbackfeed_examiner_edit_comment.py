import mock
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class TestFeedbackFeedEditGroupComment(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = feedbackfeed_examiner.GroupCommentEditView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_active_period(self):
        return baker.make_recipe('devilry.apps.core.period_active')

    def __make_examiner_for_user(self, user, group):
        return baker.make('core.Examiner',
                          assignmentgroup=group,
                          relatedexaminer=baker.make('core.RelatedExaminer', user=user))

    def test_get_no_group_comment_pk_raises_404(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser
            )

    def test_get_group_comment_does_not_exist_404(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': 1}
            )

    def test_get_other_users_comment_raises_404(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': groupcomment.id})

    def test_post_other_users_comment_raises_404(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  text='unedited',
                                  feedback_set=testfeedbackset)
        with self.assertRaises(Http404):
            self.mock_http302_postrequest(
                cradmin_role=testgroup,
                requestuser=testuser,
                viewkwargs={'pk': groupcomment.id},
                requestkwargs={
                    'data': {
                        'text': 'unedited'
                    }
                })

    def test_post_initial_empty_comment_can_be_edited(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            },
            messagesmock=messagesmock)
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        edit_history = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 1)
        self.assertEqual('edited', db_comment.text)
        self.assertEqual('', edit_history.pre_edit_text)
        self.assertEqual('edited', edit_history.post_edit_text)
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'Comment updated!', '')

    def test_post_identical_texts_does_not_save_comment(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'unedited'
                }
            },
            messagesmock=messagesmock)
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 0)
        self.assertEqual('unedited', db_comment.text)
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'No changes, comment not updated', '')

    def test_post_comment_save(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            },
            messagesmock=messagesmock
        )
        messagesmock.add.assert_called_once_with(messages.SUCCESS, 'Comment updated!', '')
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 1)
        edit_history_entry = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(edit_history_entry.group_comment.id, groupcomment.id)
        self.assertEqual(edit_history_entry.pre_edit_text, 'unedited')
        self.assertEqual(edit_history_entry.post_edit_text, 'edited')
        self.assertEqual('edited', db_comment.text)

    def test_post_comment_visible_to_everyone_history_visibility(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            },
            messagesmock=messagesmock)
        edit_history_entry = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(edit_history_entry.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def test_post_comment_visible_to_examiners_and_admin_history_visibility(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            },
            messagesmock=messagesmock)
        edit_history_entry = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(edit_history_entry.visibility,
                         group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)

    def test_post_comment_private_history_visibility(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  part_of_grading=True,
                                  visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                  feedback_set=testfeedbackset)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited'
                }
            },
            messagesmock=messagesmock)
        edit_history_entry = group_models.GroupCommentEditHistory.objects.get()
        self.assertEqual(edit_history_entry.visibility, group_models.GroupComment.VISIBILITY_PRIVATE)

    def test_post_comment_save_continue_edit(self):
        testgroup = baker.make('core.AssignmentGroup', parentnode__parentnode=self.__make_active_period())
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_examiner_for_user(user=testuser, group=testgroup)
        testfeedbackset = group_baker.feedbackset_first_attempt_unpublished(group=testgroup)
        groupcomment = baker.make('devilry_group.GroupComment',
                                  user=testuser,
                                  user_role='examiner',
                                  text='unedited',
                                  feedback_set=testfeedbackset)
        self.mock_http302_postrequest(
            cradmin_role=testgroup,
            requestuser=testuser,
            viewkwargs={'pk': groupcomment.id},
            requestkwargs={
                'data': {
                    'text': 'edited',
                    'submit-save-and-continue-editing': '',
                }
            },
        )
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 1)
        db_comment = group_models.GroupComment.objects.get(id=groupcomment.id)
        self.assertEqual('edited', db_comment.text)
