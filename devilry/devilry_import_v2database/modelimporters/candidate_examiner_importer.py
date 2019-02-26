import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core.models import Examiner, RelatedExaminer, Candidate, RelatedStudent, AssignmentGroup
from devilry.devilry_import_v2database import modelimporter


class ImporterMixin(object):
    def get_related_user_model_class(self):
        raise NotImplementedError()

    def _get_user_from_id(self, user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist():
            raise modelimporter.ModelImporterException(
                'User with id {} does not exist.'.format(user_id))
        return user

    def _get_assignment_group_from_id(self, assignment_group_id):
        try:
            assignment_group = AssignmentGroup.objects.get(id=assignment_group_id)
        except AssignmentGroup.DoesNotExist():
            raise modelimporter.ModelImporterException(
                'AssignmentGroup with id {} does not exist.'.format(assignment_group_id))
        return assignment_group

    def _get_related_user(self, period, user):
        related_user_class = self.get_related_user_model_class()
        try:
            related_user = related_user_class.objects.get(period=period, user=user)
        except related_user_class.DoesNotExist:
            return None
        return related_user

    def _create_related_user(self, user, period, **kwargs):
        related_user = self.get_related_user_model_class()(
            user=user,
            period=period,
            active=False,
            **kwargs
        )
        if self.should_clean():
            related_user.full_clean()
        related_user.save()
        return related_user


class ExaminerImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return Examiner

    def get_related_user_model_class(self):
        return RelatedExaminer

    def _create_examiner_from_object_dict(self, object_dict):
        examiner = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=examiner,
            object_dict=object_dict,
            attributes=[
                'pk'
            ]
        )
        user = self._get_user_from_id(user_id=object_dict['fields']['user'])
        assignment_group = self._get_assignment_group_from_id(
            assignment_group_id=object_dict['fields']['assignmentgroup'])
        related_examiner = self._get_related_user(period=assignment_group.parentnode.parentnode, user=user)
        if not related_examiner:
            examiner.relatedexaminer = self._create_related_user(
                user=user,
                period=assignment_group.parentnode.parentnode
            )
        else:
            examiner.relatedexaminer = related_examiner
        examiner.assignmentgroup = assignment_group
        if self.should_clean():
            examiner.full_clean()
        examiner.save()
        self.log_create(model_object=examiner, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2examiner_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print(('Would import: {}'.format(pprint.pformat(object_dict))))
            else:
                self._create_examiner_from_object_dict(object_dict=object_dict)


class CandidateImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return Candidate

    def get_related_user_model_class(self):
        return RelatedStudent

    def _create_candidate_from_object_dict(self, object_dict):
        candidate = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=candidate,
            object_dict=object_dict,
            attributes=[
                'pk',
                'candidate_id'
            ]
        )
        user = self._get_user_from_id(user_id=object_dict['fields']['student'])
        assignment_group = self._get_assignment_group_from_id(
            assignment_group_id=object_dict['fields']['assignment_group'])
        related_student = self._get_related_user(period=assignment_group.parentnode.parentnode, user=user)
        if not related_student:
            candidate.relatedstudent = self._create_related_user(
                user=user,
                period=assignment_group.parentnode.parentnode
            )
        else:
            candidate.relatedstudent = related_student
        candidate.assignment_group = assignment_group
        if self.should_clean():
            candidate.full_clean()
        candidate.save()
        self.log_create(model_object=candidate, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2candidate_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print(('Would import: {}'.format(pprint.pformat(object_dict))))
            else:
                self._create_candidate_from_object_dict(object_dict=object_dict)
