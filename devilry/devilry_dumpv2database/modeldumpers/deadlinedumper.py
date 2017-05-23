from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Deadline


class DeadlineDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Deadline

    def optimize_queryset(self, queryset):
        queryset = queryset.select_related('user')
        return queryset

    def serialize_delivery_model_object(self, deadline):
        return {}

    def serialize_model_object(self, obj):
        serialized = super(DeadlineDumper, self).serialize_model_object(obj=obj)
        return serialized
