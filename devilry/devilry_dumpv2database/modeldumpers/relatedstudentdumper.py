from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import RelatedStudent


class RelatedStudentDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return RelatedStudent

    def serialize_model_object(self, obj):
        serialized = super(RelatedStudentDumper, self).serialize_model_object(obj=obj)
        return serialized
