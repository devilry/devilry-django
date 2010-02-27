from models import *
#from models import Node, Subject, Period, Assignment, \
        #Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin
from django.db.models import Q
from django import forms



class BaseNodeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path', 'admins_unicode')
    search_fields = ['short_name', 'long_name']

    def queryset(self, request):
        if not request.user.is_superuser and hasattr(self.model, 'admin_changelist_qryset'):
            return self.model.admin_changelist_qryset(request.user)
        else:
            return super(BaseNodeAdmin, self).queryset(request)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request:
            meta = self.model._meta
            perm = '%s.%s' % (meta.app_label, meta.get_add_permission())
            if request.user.has_perm(perm):
                db_field.rel.limit_choices_to = self.model._parentnode_cls.qry_where_is_admin(request.user)
        return db_field.formfield(**kwargs)


    def get_readonly_fields(self, request, obj=None):
        if obj:
            meta = self.model._meta
            perm = '%s.%s' % (meta.app_label, meta.get_add_permission())
            if not self.model.user_has_model_perm(request.user, perm):
                r = [self.model._parentnode_field]
                r.extend(self.readonly_fields)
                print r
                return r
        return self.readonly_fields



class NodeAdministatorInline(admin.TabularInline):
    model = NodeAdministator
    extra = 1
class NodeAdmin(BaseNodeAdmin):
    inlines = (NodeAdministatorInline,)

    @classmethod
    def get_admnodes(cls, user):
        admnodes = Node.objects.filter(admins=user)
        l = []
        def add_admnodes(admnodes):
            for a in admnodes.all():
                l.append(a.id)
                add_admnodes(a.node_set)
        add_admnodes(admnodes)
        return l


class SubjectAdministatorInline(admin.TabularInline):
    model = SubjectAdministator
    extra = 1
class SubjectAdmin(BaseNodeAdmin):
    inlines = (SubjectAdministatorInline,)


class PeriodAdministatorInline(admin.TabularInline):
    model = PeriodAdministator
    extra = 1
class PeriodAdmin(BaseNodeAdmin):
    list_display = ['subject', 'short_name', 'start_time', 'end_time', 'admins_unicode']
    search_fields = ['short_name', 'long_name', 'subject__short_name']
    list_filter = ['start_time', 'end_time']
    ordering = ['subject']
    inlines = (PeriodAdministatorInline,)


class AssignmentAdministatorInline(admin.TabularInline):
    model = AssignmentAdministator
    extra = 1
class AssignmentAdmin(BaseNodeAdmin):
    inlines = [AssignmentAdministatorInline]



class DeliveryStudentInline(admin.TabularInline):
    model = DeliveryStudent
    extra = 1
class DeliveryExaminerInline(admin.TabularInline):
    model = DeliveryExaminer
    extra = 1
class DeliveryAdmin(admin.ModelAdmin):
    inlines = (DeliveryStudentInline, DeliveryExaminerInline)



class FileMetaInline(admin.TabularInline):
    model = FileMeta
    extra = 1
class DeliveryCandidateAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'id']
    inlines = (FileMetaInline,)


admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)

admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DeliveryCandidate, DeliveryCandidateAdmin)
