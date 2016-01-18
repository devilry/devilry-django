import htmls
import mock
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group import models as  group_models
from devilry.devilry_group.tests.feedbackfeed import test_feedbackfeed_common
from devilry.devilry_group.views import feedbackfeed_examiner
from devilry.apps.core import models as core_models


class TestFeedbackfeedExaminerFeedback(TestCase, test_feedbackfeed_common.TestFeedbackFeedMixin):
    viewclass = feedbackfeed_examiner.ExaminerFeedbackView

    def test_get(self):
        examiner = mommy.make('core.Examiner')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          examiner.assignmentgroup.assignment.get_path())

    def test_get_passedfailed_form_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.comment-form-container'))
        self.assertTrue(mockresponse.selector.exists('#div_id_passed'))

    def test_get_points_form_grade_option(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment),
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.comment-form-container'))
        self.assertTrue(mockresponse.selector.exists('#div_id_points'))

    def test_get_feedbackfeed_examiner_can_see_feedback_and_discuss_in_header(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                               assignmentgroup=group,
                               relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-feedback-button'))
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-discuss-button'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_for_examiners_and_admins_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_publish_feedback'))

    def test_get_feedbackfeed_examiner_wysiwyg_get_comment_choise_add_comment_to_feedbackdraft_button(self):
        examiner = mommy.make('core.Examiner')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=examiner.assignmentgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=feedbackset.group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('#submit-id-examiner_add_comment_to_feedback_draft'))

    def test_get_examiner_can_see_student_comment(self):
        group = mommy.make('core.AssignmentGroup')
        student = mommy.make('core.Candidate',
                             assignment_group=group,
                             relatedstudent=mommy.make('core.RelatedStudent', user__fullname='Jane Doe'),)
        examiner = mommy.make('core.Examiner', assignmentgroup=group)
        mommy.make('devilry_group.GroupComment',
                   user=student.relatedstudent.user,
                   user_role='student',
                   published_datetime=timezone.now() - timezone.timedelta(days=1),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner.assignmentgroup,
                                                          requestuser=examiner.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(student.relatedstudent.user.fullname, name)

    def test_get_feedbackfeed_examiner_can_see_other_examiner_comment_visible_to_everyone(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner1 = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer'))
        examiner2 = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner2.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=timezone.now(),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=examiner1.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner2.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_examiner_can_see_other_examiner_comment_visible_to_examiner_and_admins(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner1 = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer'))
        examiner2 = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner2.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   published_datetime=timezone.now(),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=examiner1.relatedexaminer.user)
        name = mockresponse.selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized
        self.assertEquals(examiner2.relatedexaminer.user.fullname, name)

    def test_get_feedbackfeed_other_examiner_can_not_see_comment_visibility_private(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        requestexaminer = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer'))
        comment_post_examiner = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'))
        mommy.make('devilry_group.GroupComment',
                   user=comment_post_examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   published_datetime=timezone.now(),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=requestexaminer.relatedexaminer.user)
        self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_get_feedbackfeed_examiner_can_see_own_private_comment(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                             assignmentgroup=group,
                             relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   published_datetime=timezone.now(),
                   feedback_set__group=group)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=group,
                                                          requestuser=examiner.relatedexaminer.user)
        self.assertTrue(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))

    def test_feedbackfeed_view_publish_feedback(self):
        group = mommy.make('core.AssignmentGroup')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   published_datetime=timezone.now(),
                   feedback_set__group=group)


    # def test_get_examiner_comment_part_of_grading_private(self):
    #     group = mommy.make('core.AssignmentGroup')
    #     examiner1 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer'),)
    #     examiner2 = mommy.make('core.Examiner',
    #                            assignmentgroup=group,
    #                            relatedexaminer=mommy.make('core.RelatedExaminer', user__fullname='Jane Doe'),)
    #     mommy.make('devilry_group.GroupComment',
    #                user=examiner2.relatedexaminer.user,
    #                user_role='examiner',
    #                part_of_grading=True,
    #                visibility=GroupComment.VISIBILITY_PRIVATE,
    #                published_datetime=timezone.now() - timezone.timedelta(days=1),
    #                feedback_set__group=group)
    #     mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=examiner1.assignmentgroup,
    #                                                       requestuser=examiner1.relatedexaminer)
    #     self.assertFalse(mockresponse.selector.exists('.devilry-group-feedbackfeed-comment'))



    def test_post_feedbackset_comment_with_text(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals(1, len(group_models.GroupComment.objects.all()))

    def test_post_feedbackset_comment_visibility_private(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', )
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a comment',
                    'examiner_add_comment_to_feedback_draft': 'unused value'
                }
            })
        self.assertEquals('private', group_models.GroupComment.objects.all()[0].visibility)

    def test_post_publish_feedbackset_before_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
        feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        self.assertIsNone(group_models.FeedbackSet.objects.all()[0].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)

    def test_post_publish_feedbackset_after_deadline_grading_system_points(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'points': 10,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(10, feedbacksets[0].grading_points)

    def test_post_publish_feedbackset_after_deadline_grading_system_passed_failed(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, feedbacksets[0].grading_points)

    def test_post_publish_feedbackset_after_deadline_test_publish_drafts_part_of_grading(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group__parentnode=assignment)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup=feedbackset.group,
                              relatedexaminer=mommy.make('core.RelatedExaminer'))
        mommy.make('devilry_group.GroupComment',
                   text='test text 1',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   feedback_set__group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   text='test text 2',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   feedback_set__group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   text='test text 3',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   feedback_set__group=feedbackset.group)
        mommy.make('devilry_group.GroupComment',
                   text='test text 4',
                   user=examiner.relatedexaminer.user,
                   user_role='examiner',
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   part_of_grading=True,
                   feedback_set__group=feedbackset.group)
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=examiner.assignmentgroup,
            requestuser=examiner.relatedexaminer.user,
            viewkwargs={'pk': feedbackset.group.id},
            requestkwargs={
                'data': {
                    'passed': True,
                    'text': 'This is a feedback',
                    'examiner_publish_feedback': 'unused value',
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertIsNotNone(feedbacksets[0].grading_published_datetime)
        self.assertEquals(1, feedbacksets[0].grading_points)

    # def test_post_feedbackset_comment_with_text_published_datetime_is_set(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet', )
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'examiner_add_public_comment': 'unused value'
    #             }
    #         })
    #     self.assertIsNotNone(models.GroupComment.objects.all()[0].published_datetime)
    #
    # def test_post_feedbackset_comment_with_text_published_datetime_is_not_set(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet', )
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'examiner_add_comment_to_feedback_draft': 'unused value'
    #             }
    #         })
    #     self.assertIsNone(models.GroupComment.objects.all()[0].published_datetime)
    #
    # def test_post_feedbackset_comment_visible_to_everyone(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet', )
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'examiner_add_public_comment': 'unused value'
    #             }
    #         })
    #     self.assertEquals('visible-to-everyone', models.GroupComment.objects.all()[0].visibility)
    #
    # def test_post_feedbackset_comment_visible_to_examiner_and_admins(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet', )
    #     examiner = mommy.make('core.Examiner',
    #                           assignmentgroup=feedbackset.group,
    #                           relatedexaminer=mommy.make('core.RelatedExaminer'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=examiner.assignmentgroup,
    #         requestuser=examiner.relatedexaminer.user,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'examiner_add_comment_for_examiners': 'unused value'
    #             }
    #         })
    #     self.assertEquals('visible-to-examiner-and-admins', models.GroupComment.objects.all()[0].visibility)

    # def test_post_comment_file(self):
    #     feedbackset = mommy.make('devilry_group.FeedbackSet')
    #     filecollection = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFileCollection',
    #     )
    #     test_file = mommy.make(
    #         'cradmin_temporaryfileuploadstore.TemporaryFile',
    #         filename='test.txt',
    #         collection=filecollection
    #     )
    #     test_file.file.save('test.txt', ContentFile('test'))
    #     self.mock_http302_postrequest(
    #         cradmin_role=feedbackset.group,
    #         viewkwargs={'pk': feedbackset.group.id},
    #         requestkwargs={
    #             'data': {
    #                 'text': 'This is a comment',
    #                 'temporary_file_collection_id': filecollection.id,
    #             }
    #         })
    #     comment_files = comment_models.CommentFile.objects.all()
    #     self.assertEquals(1, len(comment_files))