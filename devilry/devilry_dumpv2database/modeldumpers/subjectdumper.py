from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Subject


class SubjectDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Subject

    def optimize_queryset(self, queryset):
        queryset = queryset.prefetch_related('admins')
        return queryset

    def serialize_model_object(self, obj):
        serialized = super(SubjectDumper, self).serialize_model_object(obj=obj)
        serialized['admin_user_ids'] = [admin.id for admin in obj.admins.all()]
        return serialized
