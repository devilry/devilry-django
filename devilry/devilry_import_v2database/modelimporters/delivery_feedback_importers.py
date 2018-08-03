import os
import pprint
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import files

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_comment.models import Comment, CommentFile
from devilry.devilry_group.models import GroupComment, FeedbackSet
from devilry.devilry_import_v2database import modelimporter
from devilry.devilry_import_v2database.modelimporters import modelimporter_utils
from devilry.devilry_import_v2database.modelimporters.modelimporter_utils import BulkCreator
from devilry.utils import datetimeutils


class CommentFileFileDoesNotExist(Exception):
    def __init__(self, filepath, comment_file):
        self.filepath = filepath
        self.comment_file = comment_file

    def __str__(self):
        message = \
            'File {filepath!r}, CommentFile.id={commentfile_id}, v2_id={v2_id!r}. ' \
            'Not writing file, this means that the CommentFile.file will be blank.'.format(
                filepath=self.filepath,
                v2_id=self.comment_file.v2_id,
                commentfile_id=self.comment_file.id)
        return message


class CommentFileIOError(Exception):
    pass


class ImporterMixin(object):
    def _get_feedback_set_from_id(self, feedback_set_id):
        try:
            feedback_set = FeedbackSet.objects.get(id=feedback_set_id)
        except FeedbackSet.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'FeedbackSet with id {} does not exist'.format(feedback_set_id))
        return feedback_set

    def _get_user_from_id(self, user_id):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'User with id {} does not exist'.format(user_id))
        return user

    def _get_user_from_id_with_fallback(self, user_id, fallback=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            return fallback
        return user


class DeliveryImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return GroupComment

    def get_model_super_class(self):
        """
        Notes::
            We use the Comment(which GroupComment inherits from) to be able to set the sequencing number
            for Comment objects.
        """
        return Comment

    def _user_is_candidate_in_group(self, assignment_group, user):
        group_queryset = AssignmentGroup.objects.filter(id=assignment_group.id).filter_user_is_candidate(user=user)
        if group_queryset.count() == 0:
            return False
        return True

    def _get_user_from_candidate_id(self, candidate_id):
        try:
            candidate = Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return None
        else:
            return candidate.relatedstudent.user

    def _create_group_comment_from_object_dict(self, object_dict):
        group_comment = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=group_comment,
            object_dict=object_dict,
            attributes=[
                'pk',
                ('pk', 'id'),
                ('time_of_delivery', 'created_datetime'),
                ('time_of_delivery', 'published_datetime')
            ]
        )
        feedback_set_id = object_dict['fields']['deadline']
        group_comment.user = self._get_user_from_candidate_id(object_dict['fields']['delivered_by'])
        group_comment.feedback_set_id = feedback_set_id
        group_comment.text = 'Delivery'
        group_comment.comment_type = GroupComment.COMMENT_TYPE_GROUPCOMMENT
        group_comment.user_role = GroupComment.USER_ROLE_STUDENT
        group_comment.v2_id = modelimporter_utils.make_flat_v2_id(object_dict)

        if self.should_clean():
            group_comment.full_clean()
        group_comment.save()
        return group_comment

    def import_models(self, fake=False):
        directory_parser = self.v2delivery_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(
            model_class=self.get_model_super_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_group_comment_from_object_dict(object_dict=object_dict)


class StaticFeedbackImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return GroupComment

    def _user_is_examiner_on_group(self, assignment_group, user):
        group_queryset = AssignmentGroup.objects\
            .filter(id=assignment_group.id)\
            .filter_user_is_examiner(user=user)
        if group_queryset.count() == 0:
            return False
        return True

    def _save_and_publish_feedback_set(self, feedback_set, published_by, grading_points, publish_datetime):
        """
        Publish Feedback.
        """
        feedback_set.grading_published_by = published_by
        feedback_set.grading_points = grading_points
        feedback_set.grading_published_datetime = publish_datetime
        if self.should_clean():
            feedback_set.full_clean()
        feedback_set.save()

    def _create_feedback_comment_files(self, group_comment, staticfeedback_id, file_infos_dict):
        """
        Create and save CommentFiles for each file uploaded by examiners in v2.
        """
        if not isinstance(file_infos_dict, dict):
            # Handle the slightly older format where the files where
            # a list, not a dict - just to avoid crashes until we
            # create a new dump. This can be removed later.
            sys.stderr.write('x')
            return []
        commentfiles = []
        for file_info_dict in file_infos_dict.values():
            mimetype = modelimporter_utils.get_mimetype_from_filename(file_info_dict['filename'])
            comment_file = CommentFile(
                comment=group_comment,
                mimetype=mimetype,
                filename=file_info_dict['filename'],
                filesize=0,
                v2_id=modelimporter_utils.make_staticfeedback_fileattachment_v2_id(
                    staticfeedback_id=staticfeedback_id,
                    attachment_id=file_info_dict['id'])
            )
            commentfiles.append(comment_file)
        return commentfiles

    def _create_group_comment_from_object_dict(self, object_dict):
        group_comment = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=group_comment,
            object_dict=object_dict,
            attributes=[
                ('save_timestamp', 'created_datetime'),
                ('save_timestamp', 'published_datetime')
            ]
        )
        feedback_set = self._get_feedback_set_from_id(feedback_set_id=object_dict['fields']['deadline_id'])
        examiner_user = self._get_user_from_id_with_fallback(object_dict['fields']['saved_by'])
        group_comment.user = examiner_user
        self._save_and_publish_feedback_set(
            feedback_set=feedback_set,
            published_by=examiner_user,
            grading_points=object_dict['fields']['points'],
            publish_datetime=datetimeutils.from_isoformat(object_dict['fields']['save_timestamp'])
        )
        group_comment.feedback_set = feedback_set
        group_comment.part_of_grading = True
        group_comment.text = object_dict['fields']['rendered_view']
        group_comment.comment_type = GroupComment.COMMENT_TYPE_GROUPCOMMENT
        group_comment.user_role = GroupComment.USER_ROLE_EXAMINER
        group_comment.v2_id = modelimporter_utils.make_flat_v2_id(object_dict)
        if self.should_clean():
            group_comment.full_clean()
        group_comment.save()
        commentfiles = self._create_feedback_comment_files(
            group_comment,
            staticfeedback_id=object_dict['pk'],
            file_infos_dict=object_dict['fields']['files'])
        self.log_create(model_object=group_comment, data=object_dict)
        return group_comment, commentfiles

    def import_models(self, fake=False):
        with BulkCreator(model_class=CommentFile) as commentfile_bulk_creator:
            for object_dict in self.v2staticfeedback_directoryparser.iterate_object_dicts():
                if fake:
                    print('Would import: {}'.format(pprint.pformat(object_dict)))
                else:
                    group_comment, commentfiles = self._create_group_comment_from_object_dict(object_dict=object_dict)
                    if commentfiles:
                        commentfile_bulk_creator.add(*commentfiles)


class FileMetaImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return CommentFile

    def _create_comment_file_from_object_id(self, object_dict):
        comment_file = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=comment_file,
            object_dict=object_dict,
            attributes=[
                'filename'
            ]
        )
        comment_id = object_dict['fields']['delivery']
        comment_file.comment_id = comment_id
        comment_file.filesize = 0
        comment_file.mimetype = modelimporter_utils.get_mimetype_from_filename(
            filename=object_dict['fields'].get('filename', None))
        comment_file.v2_id = modelimporter_utils.make_flat_v2_id(object_dict)
        return comment_file

    def import_models(self, fake=False):
        with BulkCreator(model_class=CommentFile) as commentfile_bulk_creator:
            for object_dict in self.v2filemeta_directoryparser.iterate_object_dicts():
                if fake:
                    print('Would import: {}'.format(pprint.pformat(object_dict)))
                else:
                    comment_file = self._create_comment_file_from_object_id(object_dict=object_dict)
                    commentfile_bulk_creator.add(comment_file)


class CommentFileContentImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return CommentFile

    def _write_file_to_commentfile(self, comment_file, filepath):
        if not os.path.exists(filepath):
            raise CommentFileFileDoesNotExist(filepath, comment_file)
        comment_file.filesize = os.stat(filepath).st_size
        fp = open(filepath, 'rb')
        comment_file.file = files.File(fp, comment_file.filename)
        if self.should_clean():
            comment_file.full_clean()
        try:
            comment_file.save()
        except IOError as error:
            raise CommentFileIOError('Failed to write CommentFile#{commentfile_id}, filepath={filepath}: {error}'.format(
                commentfile_id=comment_file.id,
                filepath=filepath,
                error=error))
        fp.close()

    def _copy_commentfile_file_from_filemeta(self, comment_file, v2idstring):
        v2_delivery_file_root = getattr(settings, 'DEVILRY_V2_DELIVERY_FILE_ROOT', None)
        if not v2_delivery_file_root:
            return
        object_dict = self.v2filemeta_directoryparser.get_object_dict_by_id(id=v2idstring)
        filepath = os.path.join(v2_delivery_file_root,
                                object_dict['fields']['relative_file_path'])
        self._write_file_to_commentfile(comment_file=comment_file,
                                        filepath=filepath)

    def _copy_commentfile_file_from_staticfeedbackfileattachment(self, comment_file, v2idstring):
        v2_media_root = getattr(settings, 'DEVILRY_V2_MEDIA_ROOT', None)
        if not v2_media_root:
            return
        staticfeedback_id, attachment_id = v2idstring.split('__')
        object_dict = self.v2staticfeedback_directoryparser.get_object_dict_by_id(id=staticfeedback_id)
        feedbackattachments = object_dict['fields'].get('files', None) or {}
        attachment = feedbackattachments[attachment_id]
        filepath = os.path.join(v2_media_root, attachment['relative_file_path'])
        self._write_file_to_commentfile(comment_file=comment_file,
                                        filepath=filepath)

    def _copy_commentfile_file(self, comment_file):
        v2model, v2idstring = comment_file.v2_id.split('__', 1)
        if v2model == 'filemeta':
            # Deliveries
            self._copy_commentfile_file_from_filemeta(
                comment_file=comment_file,
                v2idstring=v2idstring)
        elif v2model == 'staticfeedbackfileattachment':
            # Attachments to feedbacks
            self._copy_commentfile_file_from_staticfeedbackfileattachment(
                comment_file=comment_file,
                v2idstring=v2idstring)
        else:
            raise ValueError('Invalid v2model: {}'.format(v2model))

    def import_models(self, fake=False):
        does_not_exist = []
        with modelimporter_utils.ProgressDots() as progressdots:
            for comment_file in CommentFile.objects.exclude(v2_id='').iterator():
                try:
                    self._copy_commentfile_file(comment_file)
                except CommentFileFileDoesNotExist as error:
                    does_not_exist.append(error)
                progressdots.increment_progress()

        if does_not_exist:
            print >> sys.stderr, 'Some of the source files did not exist.'
            for error in does_not_exist:
                print >> sys.stderr, '- {}'.format(error)
