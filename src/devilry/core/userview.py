from django.contrib import admin
from devilry.auth import authadmin
from devilry.core.models import AssignmentGroup, Delivery, FileMeta

class FileMetaInline(admin.TabularInline):
    model = FileMeta
    extra = 1

class DeliveryAdmin(authadmin.ModelAdmin):
    inlines = (FileMetaInline,)
    list_display = ['time_of_delivery', 'assignment_group']
    exclude = ['time_of_delivery']

    def assignment(self, obj):
        return obj.assignment_group.parentnode

    def queryset(self, request):
        return self.model.get_changelist(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True



site = admin.sites.AdminSite(name='userview')
site.register(Delivery, DeliveryAdmin)
