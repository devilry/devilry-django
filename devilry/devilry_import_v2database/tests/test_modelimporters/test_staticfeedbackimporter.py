import os
import tempfile
import unittest

import shutil
from django import test
from django.conf import settings
from devilry.utils import datetimeutils

from model_bakery import baker

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import FeedbackSet, GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers \
    import StaticFeedbackImporter, DeliveryImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestStaticFeedbackImporterImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        self.v2_media_root_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestStaticFeedbackImporterImporter, self).tearDown()
        shutil.rmtree(self.v2_media_root_temp_dir)

    def _create_staticfeedback_dict(self, feedback_set, file_info_dict=None, examiner_user_id=None):
        return {
            'pk': 1,
            'model': 'core.staticfeedback',
            'fields': {
                'is_passing_grade': True,
                'grade': '2/4',
                'saved_by': examiner_user_id,
                'delivery': 1,
                'points': 2,
                'files': file_info_dict or {},
                'deadline_id': feedback_set.id,
                'save_timestamp': '2017-05-15T11:04:46.817',
                'rendered_view': '<p>Quo tempore facilis eos suscipit eum doloremque libero'
                                  ' veniam nisi?</p>\n<p>Magnam mollitia alias consequatur nisi'
                                  ' nam error dolor laboriosam aperiam? Nihil eligendi voluptatem,'
                                  ' eveniet iure officiis amet laborum debitis nisi in, '
                                  'molestias similique vero quos beatae obcaecati neque laudantium '
                                  'suscipit rerum repudiandae, facilis doloribus autem molestias '
                                  'asperiores perferendis est delectus alias porro laboriosam culpa, '
                                  'iusto ut aliquid et? Id iusto dolor consequatur necessitatibus explicabo '
                                  'repellendus, suscipit nisi non.</p>\n<p>Quas natus id nulla pariatur'
                                  ' similique ducimus mollitia ea tenetur veniam fugiat, rerum temporibus '
                                  'tempore eaque nemo at, nihil dolores ad ducimus delectus quasi nesciunt '
                                  'illo, aspernatur ullam officia aperiam officiis harum repellat pariatur '
                                  'quaerat deserunt sint. Debitis nam deserunt autem voluptas? Debitis libero'
                                  ' beatae deserunt et ullam expedita aliquid inventore autem nam veniam, '
                                  'dolore rem ea voluptatibus placeat explicabo.</p>'
            }
        }

    def test_importer(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(FeedbackSet.objects.count(), 1)
        self.assertEqual(GroupComment.objects.count(), 1)

    def test_importer_feedback_set(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.feedback_set, test_feedbackset)

    def test_importer_user(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.user, test_examiner_user)

    def test_importer_user_role(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.user_role, GroupComment.USER_ROLE_EXAMINER)

    def test_importer_text(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.text, staticfeedback_data_dict['fields']['rendered_view'])

    def test_importer_comment_type(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.comment_type, GroupComment.COMMENT_TYPE_GROUPCOMMENT)

    def test_importer_comment_is_part_of_grading(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertTrue(comment.part_of_grading)

    def test_importer_published_datetime(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id
        )
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(
            comment.published_datetime,
            datetimeutils.from_isoformat(staticfeedback_data_dict['fields']['save_timestamp'])
        )

    def test_importer_feedback_set_grading_published_datetime(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id
        )
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        feedback_set = GroupComment.objects.first().feedback_set
        self.assertEqual(
            feedback_set.grading_published_datetime,
            datetimeutils.from_isoformat(staticfeedback_data_dict['fields']['save_timestamp']))

    def test_importer_feedback_set_grading_points(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id
        )
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        feedback_set = GroupComment.objects.first().feedback_set
        self.assertEqual(feedback_set.grading_points, staticfeedback_data_dict['fields']['points'])

    def test_importer_feedback_set_grading_published_by(self):
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id
        )
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        feedback_set = GroupComment.objects.first().feedback_set
        self.assertEqual(feedback_set.grading_published_by, test_examiner_user)

    def test_importer_comment_file_attributes(self):
        with self.settings(DEVILRY_V2_MEDIA_ROOT=self.v2_media_root_temp_dir):
            test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
            test_group = baker.make('core.AssignmentGroup')
            baker.make('core.Examiner',
                       assignmentgroup=test_group,
                       relatedexaminer__user=test_examiner_user,
                       relatedexaminer__period=test_group.parentnode.parentnode)
            test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
            self.create_v2dump(
                model_name='core.staticfeedback',
                data=self._create_staticfeedback_dict(
                    feedback_set=test_feedbackset,
                    examiner_user_id=test_examiner_user.id,
                    file_info_dict={
                        '1': {
                            'id': 1,
                            'filename': 'test.py',
                            'relative_file_path': 'test.py',
                        }
                    })
            )
            StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
            self.assertEqual(CommentFile.objects.count(), 1)
            comment_file = CommentFile.objects.first()
            self.assertEqual(comment_file.filename, 'test.py')
            self.assertEqual(comment_file.mimetype, 'text/x-python')


@unittest.skip('Not relevant anymore, keep for history.')
class TestDeliveryAndStaticFeedbackImporterImporter(ImporterTestCaseMixin, test.TestCase):
    """
    Tests to make sure StaticFeedbacks are created with an auto incremented sequence number that should
    start at the Delivery meta datas max_id.

    We need to do this because deliveries and feedbacks are to different models in Devilry V2, but they will both
    be created as GroupComments in Devilry V3. So if we kept the primary keys for both Delivery and
    StaticFeedback, these would eventually crash when creating the GroupComments.

    The GroupComments for a Delivery will keep the primary key from Devilry V2, and the GroupComments for feedbacks
    will get an auto incremented sequence number starting at the Delivery meta data max_id.

    Each test will be a kind of simulation, and represents the order in which the importers for
    Delivery and StaticFeedback must be run.
    """
    def _create_model_meta_for_delivery(self):
        return {
            'model_class_name': 'Delivery',
            'max_id': 143,
            'app_label': 'core'
        }

    def _create_delivery_dict(self, feedback_set, candidate_id=None):
        return {
            'pk': 3,
            'model': 'core.delivery',
            'fields': {
                'delivery_type': 0,
                'alias_delivery': None,
                'successful': True,
                'number': 1,
                'delivered_by': candidate_id,
                'last_feedback': 3,
                'deadline': feedback_set.id,
                'copy_of': None,
                'time_of_delivery': '2016-04-10T07:04:00'
            },
        }

    def _create_staticfeedback_dict(self, feedback_set, examiner_user_id=None):
        return {
            'pk': 1,
            'model': 'core.staticfeedback',
            'fields': {
                'is_passing_grade': True,
                'grade': '2/4',
                'saved_by': examiner_user_id,
                'delivery': 1,
                'points': 2,
                'files': {},
                'deadline_id': feedback_set.id,
                'save_timestamp': '2017-05-15T11:04:46.817',
                'rendered_view': '<p>Quo tempore facilis eos suscipit eum doloremque libero'
                                  ' veniam nisi?</p>\n<p>Magnam mollitia alias consequatur nisi'
                                  ' nam error dolor laboriosam aperiam? Nihil eligendi voluptatem,'
                                  ' eveniet iure officiis amet laborum debitis nisi in, '
                                  'molestias similique vero quos beatae obcaecati neque laudantium '
                                  'suscipit rerum repudiandae, facilis doloribus autem molestias '
                                  'asperiores perferendis est delectus alias porro laboriosam culpa, '
                                  'iusto ut aliquid et? Id iusto dolor consequatur necessitatibus explicabo '
                                  'repellendus, suscipit nisi non.</p>\n<p>Quas natus id nulla pariatur'
                                  ' similique ducimus mollitia ea tenetur veniam fugiat, rerum temporibus '
                                  'tempore eaque nemo at, nihil dolores ad ducimus delectus quasi nesciunt '
                                  'illo, aspernatur ullam officia aperiam officiis harum repellat pariatur '
                                  'quaerat deserunt sint. Debitis nam deserunt autem voluptas? Debitis libero'
                                  ' beatae deserunt et ullam expedita aliquid inventore autem nam veniam, '
                                  'dolore rem ea voluptatibus placeat explicabo.</p>'
            }
        }

    def test_importer(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id
        )
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(GroupComment.objects.count(), 2)

    def test_importer_feedback_comments_id_starts_at_max_id(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id),
            model_meta=self._create_model_meta_for_delivery()
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id
            )
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(GroupComment.objects.count(), 2)
        delivery_comment = GroupComment.objects.filter(user_role=GroupComment.USER_ROLE_STUDENT).first()
        feedback_comment = GroupComment.objects.filter(user_role=GroupComment.USER_ROLE_EXAMINER).first()
        self.assertEqual(delivery_comment.pk, 3)
        self.assertEqual(delivery_comment.id, 3)
        self.assertEqual(feedback_comment.pk, self._create_model_meta_for_delivery()['max_id']+1)
        self.assertEqual(feedback_comment.id, self._create_model_meta_for_delivery()['max_id']+1)
