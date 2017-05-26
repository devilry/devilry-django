from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import StaticFeedback


class StaticFeedbackDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return StaticFeedback

    def serialize_model_object(self, obj):
        serialized = super(StaticFeedbackDumper, self).serialize_model_object(obj=obj)
        serialized['fields']['deadline_id'] = obj.delivery.deadline.id
        return serialized
