from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import AssignmentGroup


class AssignmentGroupDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return AssignmentGroup

    def serialize_model_object(self, obj):
        serialized = super(AssignmentGroupDumper, self).serialize_model_object(obj=obj)
        if serialized['fields']['name'] is None:
            serialized['fields']['name'] = ''
        return serialized
