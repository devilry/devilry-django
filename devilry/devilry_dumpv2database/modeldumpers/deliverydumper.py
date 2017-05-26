from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import Delivery


class DeliveryDumper(modeldumper.ModelDumper):
    def get_model_class(self):
        return Delivery

    def serialize_model_object(self, obj):
        if obj.delivered_by is None:
            obj.delivered_by = obj.deadline.assignment_group.candidates.first()
        serialized = super(DeliveryDumper, self).serialize_model_object(obj=obj)
        return serialized


# class DeliveryDumper(modeldumper.ModelDumper):
#     def get_model_class(self):
#         return Delivery
#
#     def _get_last_delivery_for_deadline(self, deadline):
#         return deadline.deliveries.order_by('-time_of_delivery').first()
#
#     def optimize_queryset(self, queryset):
#         last_delivery_ids_list = [self._get_last_delivery_for_deadline(delivery.deadline).id
#                                   for delivery in queryset.all()]
#         return queryset.filter(id__in=last_delivery_ids_list)
#
#     def serialize_model_object(self, obj):
#         serialized = super(DeliveryDumper, self).serialize_model_object(obj=obj)
#         if not obj.last_feedback:
#             serialized['last_feedback'] = None
#         else:
#             serialized['last_feedback'] = super(DeliveryDumper, self).serialize_model_object(obj=obj.last_feedback)
#         if not serialized['fields']['delivered_by']:
#             serialized['fields']['delivered_by'] = obj.deadline.assignment_group.candidates.first().student.id
#         return serialized
