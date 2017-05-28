import os

from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import FeedbackSet, GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers \
    import StaticFeedbackImporter, DeliveryImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestStaticFeedbackImporterImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_staticfeedback_dict(self, feedback_set, file_info_list=None, examiner_user_id=None):
        return {
            'pk': 1,
            'model': 'core.staticfeedback',
            'fields': {
                'is_passing_grade': True,
                'grade': '2/4',
                'saved_by': examiner_user_id,
                'delivery': 1,
                'points': 2,
                'files': [] if not file_info_list else file_info_list,
                'deadline_id': feedback_set.id,
                'save_timestamp': '2017-05-15T11:04:46.817',
                'rendered_view': u'<p>Quo tempore facilis eos suscipit eum doloremque libero'
                                  u' veniam nisi?</p>\n<p>Magnam mollitia alias consequatur nisi'
                                  u' nam error dolor laboriosam aperiam? Nihil eligendi voluptatem,'
                                  u' eveniet iure officiis amet laborum debitis nisi in, '
                                  u'molestias similique vero quos beatae obcaecati neque laudantium '
                                  u'suscipit rerum repudiandae, facilis doloribus autem molestias '
                                  u'asperiores perferendis est delectus alias porro laboriosam culpa, '
                                  u'iusto ut aliquid et? Id iusto dolor consequatur necessitatibus explicabo '
                                  u'repellendus, suscipit nisi non.</p>\n<p>Quas natus id nulla pariatur'
                                  u' similique ducimus mollitia ea tenetur veniam fugiat, rerum temporibus '
                                  u'tempore eaque nemo at, nihil dolores ad ducimus delectus quasi nesciunt '
                                  u'illo, aspernatur ullam officia aperiam officiis harum repellat pariatur '
                                  u'quaerat deserunt sint. Debitis nam deserunt autem voluptas? Debitis libero'
                                  u' beatae deserunt et ullam expedita aliquid inventore autem nam veniam, '
                                  u'dolore rem ea voluptatibus placeat explicabo.</p>'
            }
        }

    def test_importer(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(FeedbackSet.objects.count(), 1)
        self.assertEquals(GroupComment.objects.count(), 1)

    def test_importer_feedback_set(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEquals(comment.feedback_set, test_feedbackset)

    def test_importer_user(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEquals(comment.user, test_examiner_user)

    def test_importer_user_role(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEquals(comment.user_role, GroupComment.USER_ROLE_EXAMINER)

    def test_importer_text(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        staticfeedback_data_dict = self._create_staticfeedback_dict(
            feedback_set=test_feedbackset,
            examiner_user_id=test_examiner_user.id)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=staticfeedback_data_dict
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEquals(comment.text, staticfeedback_data_dict['fields']['rendered_view'])

    def test_importer_comment_type(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id)
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEquals(comment.comment_type, GroupComment.COMMENT_TYPE_GROUPCOMMENT)

    def test_importer_published_datetime(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(
            comment.published_datetime,
            parse_datetime(staticfeedback_data_dict['fields']['save_timestamp'])
        )

    def test_importer_feedback_set_grading_published_datetime(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(
            feedback_set.grading_published_datetime,
            parse_datetime(staticfeedback_data_dict['fields']['save_timestamp']))

    def test_importer_feedback_set_grading_points(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(feedback_set.grading_points, staticfeedback_data_dict['fields']['points'])

    def test_importer_feedback_set_grading_published_by(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(feedback_set.grading_published_by, test_examiner_user)

    def test_importer_comment_file_attributes(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        v2_file = open('test.py', 'wb')
        v2_file.write("print('Hello, world!')")
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id,
                file_info_list=[{
                    'filename': 'test.py',
                    'absolute_file_path': abs_path,
                    'size': os.stat(abs_path).st_size,
                    'mimetype': 'text/x-python'
                }])
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(CommentFile.objects.count(), 1)
        comment_file = CommentFile.objects.first()
        self.assertEquals(comment_file.filename, 'test.py')
        self.assertEquals(comment_file.mimetype, 'text/x-python')
        self.assertEquals(comment_file.filesize, os.stat(abs_path).st_size)
        self.assertEquals(comment_file.file.read(), "print('Hello, world!')")
        os.remove(abs_path)

    def test_importer_comment_file_comment(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        v2_file = open('test.py', 'wb')
        v2_file.write("print('Hello, world!')")
        v2_file.close()
        abs_path = os.path.abspath(v2_file.name)
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id,
                file_info_list=[{
                    'filename': 'test.py',
                    'absolute_file_path': abs_path,
                    'size': os.stat(abs_path).st_size,
                    'mimetype': 'text/x-python'
                }])
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(CommentFile.objects.count(), 1)
        self.assertEquals(GroupComment.objects.count(), 1)
        comment_file = CommentFile.objects.first()
        comment_file_group_comment = GroupComment.objects.get(id=comment_file.comment.id)
        group_comment = GroupComment.objects.first()
        self.assertEquals(comment_file_group_comment, group_comment)
        os.remove(abs_path)

    def test_importer_multiple_feedback_files(self):
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        v2_file1 = open('test_file_1.py', 'wb')
        v2_file1.write("print('Hello, world!')")
        v2_file1.close()
        abs_path1 = os.path.abspath(v2_file1.name)
        v2_file2 = open('test_file_2.py', 'wb')
        v2_file2.write("print('Hello, world!')")
        v2_file2.close()
        abs_path2 = os.path.abspath(v2_file2.name)
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.staticfeedback',
            data=self._create_staticfeedback_dict(
                feedback_set=test_feedbackset,
                examiner_user_id=test_examiner_user.id,
                file_info_list=[
                    {
                        'filename': 'test_file_1.py',
                        'absolute_file_path': abs_path1,
                        'size': os.stat(abs_path1).st_size,
                        'mimetype': 'text/x-python'
                    },
                    {
                        'filename': 'test_file_2.py',
                        'absolute_file_path': abs_path2,
                        'size': os.stat(abs_path2).st_size,
                        'mimetype': 'text/x-python'
                    }
                ])
        )
        StaticFeedbackImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(CommentFile.objects.count(), 2)
        self.assertEquals(GroupComment.objects.count(), 1)
        group_comment = GroupComment.objects.first()
        comment_file_names_list = [comment_file.filename for comment_file in CommentFile.objects.all()]
        for comment_file in group_comment.commentfile_set.all():
            self.assertIn(comment_file.filename, comment_file_names_list)
        os.remove(abs_path1)
        os.remove(abs_path2)


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
                'files': [],
                'deadline_id': feedback_set.id,
                'save_timestamp': '2017-05-15T11:04:46.817',
                'rendered_view': u'<p>Quo tempore facilis eos suscipit eum doloremque libero'
                                  u' veniam nisi?</p>\n<p>Magnam mollitia alias consequatur nisi'
                                  u' nam error dolor laboriosam aperiam? Nihil eligendi voluptatem,'
                                  u' eveniet iure officiis amet laborum debitis nisi in, '
                                  u'molestias similique vero quos beatae obcaecati neque laudantium '
                                  u'suscipit rerum repudiandae, facilis doloribus autem molestias '
                                  u'asperiores perferendis est delectus alias porro laboriosam culpa, '
                                  u'iusto ut aliquid et? Id iusto dolor consequatur necessitatibus explicabo '
                                  u'repellendus, suscipit nisi non.</p>\n<p>Quas natus id nulla pariatur'
                                  u' similique ducimus mollitia ea tenetur veniam fugiat, rerum temporibus '
                                  u'tempore eaque nemo at, nihil dolores ad ducimus delectus quasi nesciunt '
                                  u'illo, aspernatur ullam officia aperiam officiis harum repellat pariatur '
                                  u'quaerat deserunt sint. Debitis nam deserunt autem voluptas? Debitis libero'
                                  u' beatae deserunt et ullam expedita aliquid inventore autem nam veniam, '
                                  u'dolore rem ea voluptatibus placeat explicabo.</p>'
            }
        }

    def test_importer(self):
        test_student_user = mommy.make(settings.AUTH_USER_MODEL)
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        candidate = mommy.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(GroupComment.objects.count(), 2)

    def test_importer_feedback_comments_id_starts_at_max_id(self):
        test_student_user = mommy.make(settings.AUTH_USER_MODEL)
        test_examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        mommy.make('core.Examiner',
                   assignmentgroup=test_group,
                   relatedexaminer__user=test_examiner_user,
                   relatedexaminer__period=test_group.parentnode.parentnode)
        candidate = mommy.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group=test_group)
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
        self.assertEquals(GroupComment.objects.count(), 2)
        delivery_comment = GroupComment.objects.filter(user_role=GroupComment.USER_ROLE_STUDENT).first()
        feedback_comment = GroupComment.objects.filter(user_role=GroupComment.USER_ROLE_EXAMINER).first()
        self.assertEquals(delivery_comment.pk, 3)
        self.assertEquals(delivery_comment.id, 3)
        self.assertEquals(feedback_comment.pk, self._create_model_meta_for_delivery()['max_id']+1)
        self.assertEquals(feedback_comment.id, self._create_model_meta_for_delivery()['max_id']+1)
