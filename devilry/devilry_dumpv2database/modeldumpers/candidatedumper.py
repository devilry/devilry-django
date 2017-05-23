from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Candidate


class CandidateDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Candidate

    def serialize_model_object(self, obj):
        serialized = super(CandidateDumper, self).serialize_model_object(obj=obj)
        return serialized
