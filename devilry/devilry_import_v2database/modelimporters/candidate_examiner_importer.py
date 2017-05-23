import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core.models import Examiner, RelatedExaminer, Candidate, RelatedStudent, AssignmentGroup
from devilry.devilry_import_v2database import modelimporter


class ImporterMixin(object):
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
        except get_user_model().DoesNotExist():
            raise modelimporter.ModelImporterException(
                'AssignmentGroup with id {} does not exist.'.format(assignment_group_id))
        return assignment_group


class ExaminerImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return Examiner

    def _create_relatedexaminer(self, user, period):
        related_examiner = RelatedExaminer(
            user=user,
            period=period
        )
        related_examiner.full_clean()
        related_examiner.save()
        return related_examiner

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
        related_examiner = self._create_relatedexaminer(user=user, period=assignment_group.parentnode.parentnode)
        examiner.relatedexaminer = related_examiner
        examiner.assignmentgroup = assignment_group
        examiner.full_clean()
        examiner.save()
        self.log_create(model_object=examiner, data=object_dict)

    def import_models(self, fake=False):
        for object_dict in self.v2examiner_directoryparser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_examiner_from_object_dict(object_dict=object_dict)


class CandidateImporter(ImporterMixin, modelimporter.ModelImporter):
    def get_model_class(self):
        return Candidate

    def _create_relatedstudent(self, user, period, **kwargs):
        related_student = RelatedStudent(
            user=user,
            period=period,
            **kwargs
        )
        related_student.full_clean()
        related_student.save()
        return related_student

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
        related_student = self._create_relatedstudent(
            user=user,
            period=assignment_group.parentnode.parentnode,
            candidate_id=object_dict['fields']['candidate_id']
        )
        candidate.relatedstudent = related_student
        candidate.assignment_group = assignment_group
        candidate.full_clean()
        candidate.save()
        self.log_create(model_object=candidate, data=object_dict)

    def import_models(self, fake=False):
        for object_dict in self.v2candidate_directoryparser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_candidate_from_object_dict(object_dict=object_dict)
