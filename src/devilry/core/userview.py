from django.contrib import admin
from devilry.auth import authadmin
from models import DeliveryGroup, Delivery, FileMeta




class DeliveryAdmin(authadmin.ModelAdmin):
    list_display = ['time_of_delivery', 'delivery_group']

    def assignment(self, obj):
        return obj.delivery_group.parentnode

    def queryset(self, request):
        return self.model.get_changelist(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


site = admin.sites.AdminSite(name='userview')
site.register(Delivery, DeliveryAdmin)
