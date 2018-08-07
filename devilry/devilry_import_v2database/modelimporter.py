from django.conf import settings
from django.db import models

from devilry.devilry_import_v2database import v2dump_directoryparsers
from devilry.devilry_import_v2database.modelimporters import modelimporter_utils
from devilry.devilry_import_v2database.models import ImportedModel
from devilry.utils import datetimeutils


class ModelImporterException(Exception):
    pass


class ModelImporter(object):
    def __init__(self, input_root, **kwargs):
        self.input_root = input_root
        self.kwargs = kwargs

    def get_model_class(self):
        """
        Get the model class.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def target_model_has_objects(self):
        if not self.get_model_class():
            # We need this when importing Node as this model
            # no longer exists in Devilry 3.0
            return False
        return self.get_model_class().objects.exists()

    def prettyformat_model_name(self):
        model_class = self.get_model_class()
        if not model_class:
            return ''
        return '{}.{}'.format(model_class._meta.app_label,
                              model_class.__name__)

    def import_models(self):
        raise NotImplementedError()

    def patch_model_from_object_dict(self, model_object, object_dict, attributes):
        for attribute in attributes:
            if isinstance(attribute, tuple):
                from_attribute, to_attribute = attribute
            else:
                from_attribute = attribute
                to_attribute = attribute
            if from_attribute == 'pk':
                value = object_dict[from_attribute]
            else:
                value = object_dict['fields'][from_attribute]
                if value:
                    field = model_object._meta.get_field(to_attribute)
                    if isinstance(field, models.DateTimeField):
                        value = datetimeutils.from_isoformat(value)
            setattr(model_object, to_attribute, value)

    def log_create(self, model_object, data):
        # imported_model = ImportedModel(
        #     content_object=model_object,
        #     content_object_id=model_object.id,
        #     data=data
        # )
        # modelimporter_utils.logger_singleton.add(imported_model)
        pass

    @property
    def v2user_directoryparser(self):
        return v2dump_directoryparsers.V2UserDirectoryParser(
            input_root=self.input_root)

    @property
    def v2subject_directoryparser(self):
        return v2dump_directoryparsers.V2SubjectDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2period_directoryparser(self):
        return v2dump_directoryparsers.V2PeriodDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2assignment_directoryparser(self):
        return v2dump_directoryparsers.V2AssignmentDirectoryParser(
            input_root=self.input_root
        )
    
    @property
    def v2node_directoryparser(self):
        return v2dump_directoryparsers.V2NodeDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2assignmentgroup_directoryparser(self):
        return v2dump_directoryparsers.V2AssignmentGroupDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2pointtogrademap_directoryparser(self):
        return v2dump_directoryparsers.V2PointToGradeMapDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2pointrangetograde_directoryparser(self):
        return v2dump_directoryparsers.V2PointRangeToGradeDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2examiner_directoryparser(self):
        return v2dump_directoryparsers.V2ExaminerDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2candidate_directoryparser(self):
        return v2dump_directoryparsers.V2CandidateDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2deadline_directoryparser(self):
        return v2dump_directoryparsers.V2DeadlineDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2relatedexaminer_directoryparser(self):
        return v2dump_directoryparsers.V2RelatedExaminerDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2relatedstudent_directoryparser(self):
        return v2dump_directoryparsers.V2RelatedStudentDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2delivery_directoryparser(self):
        return v2dump_directoryparsers.V2DeliveryDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2staticfeedback_directoryparser(self):
        return v2dump_directoryparsers.V2StaticFeedbackDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2filemeta_directoryparser(self):
        return v2dump_directoryparsers.V2FileMetaDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2qualifiesforexam_status_directoryparser(self):
        return v2dump_directoryparsers.V2QualifiesForExamStatusDirectoryParser(
            input_root=self.input_root
        )

    @property
    def v2qualifiesforexamfinalexam_directoryparser(self):
        return v2dump_directoryparsers.V2QualifiesForFinalExamDirectoryParser(
            input_root=self.input_root
        )

    def should_clean(self):
        return getattr(settings, 'DEVILRY_V2_DATABASE_SHOULD_CLEAN', False)
