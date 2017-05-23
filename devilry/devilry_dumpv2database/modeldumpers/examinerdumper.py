from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Examiner, RelatedExaminer


class ExaminerDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Examiner

    def serialize_model_object(self, obj):
        serialized = super(ExaminerDumper, self).serialize_model_object(obj=obj)
        return serialized
