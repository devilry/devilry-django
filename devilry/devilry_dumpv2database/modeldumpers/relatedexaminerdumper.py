from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import RelatedExaminer


class RelatedExaminerDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return RelatedExaminer

    def serialize_model_object(self, obj):
        serialized = super(RelatedExaminerDumper, self).serialize_model_object(obj=obj)
        return serialized
