from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Examiner


class ExaminerDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Examiner

    # def optimize_queryset(self, queryset):
    #     queryset = queryset.select_related('user')
    #     return queryset
    #
    # def serialize_model_object(self, obj):
    #     serialized = super(ExaminerDumper, self).serialize_model_object(obj=obj)
    #     return serialized
