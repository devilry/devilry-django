from devilry.apps.core.models import Assignment
from devilry.devilry_dumpv2database import modeldumper


class AssignmentDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Assignment

    def optimize_queryset(self, queryset):
        queryset = queryset.prefetch_related('admins')
        return queryset

    def serialize_model_object(self, obj):
        if obj.first_deadline is None:
            obj.first_deadline = obj.parentnode.end_time
        serialized = super(AssignmentDumper, self).serialize_model_object(obj=obj)
        serialized['admin_user_ids'] = [admin.id for admin in obj.admins.all()]
        return serialized
