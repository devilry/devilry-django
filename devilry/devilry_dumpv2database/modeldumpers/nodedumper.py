from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Node


class NodeDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Node

    def optimize_queryset(self, queryset):
        queryset = queryset.prefetch_related('admins')
        return queryset

    def _get_subject_id_list(self, subject_queryset):
        return [subject.id for subject in subject_queryset.all()]

    def _add_subject_ids(self, node):
        subject_ids = []
        subject_ids.extend(
            self._get_subject_id_list(node.subjects.all())
        )
        for childnode in node.iter_childnodes():
            subject_ids.extend(self._get_subject_id_list(childnode.subjects))
        return subject_ids

    def serialize_model_object(self, obj):
        serialized = super(NodeDumper, self).serialize_model_object(obj=obj)
        serialized['subject_ids'] = self._add_subject_ids(node=obj)
        serialized['admin_user_ids'] = [admin.id for admin in obj.admins.all()]
        return serialized
