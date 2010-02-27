from models import *
#from models import Node, Subject, Period, Assignment, \
        #Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin
from django.db.models import Q



class LimitAccess:
    #def queryset(self, request):
        #""" Limit administrators to superusers, and administators on this
        #node or any of the parent-nodes. """
        #if request.user.is_superuser:
            #return self.get_modelcls().objects
        #else:
            #return self.get_instances_where_admin(request.user)

    def get_instances_where_admin(self, user):
        raise NotImplementedError()

    def get_modelcls(self):
        raise NotImplementedError()



class BaseNodeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path', 'admins_unicode')
    search_fields = ['short_name', 'long_name']

    def queryset(self, request):
        if not request.user.is_superuser and hasattr(self.model, 'admin_changelist_qryset'):
            return self.model.admin_changelist_qryset(request.user)
        else:
            return super(BaseNodeAdmin, self).queryset(request)


    #def has_add_permission(self, request):
        #"Returns True if the given request has permission to add an object."
        #return True

    #def has_change_permission(self, request, obj=None):
        #"""
        #Returns True if the given request has permission to change the given
        #Django model instance.

        #If `obj` is None, this should return True if the given request has
        #permission to change *any* object of the given type.
        #"""
        #return True

    #def has_delete_permission(self, request, obj=None):
        #"""
        #Returns True if the given request has permission to change the given
        #Django model instance.

        #If `obj` is None, this should return True if the given request has
        #permission to delete *any* object of the given type.
        #"""
        #return True

    #def get_model_perms(self, request):
        #"""
        #Returns a dict of all perms for this model. This dict has the keys
        #``add``, ``change``, and ``delete`` mapping to the True/False for each
        #of those actions.
        #"""
        #return {
            #'add': True,
            #'change': True,
            #'delete': True,
        #}


class NodeAdministatorInline(admin.TabularInline):
    model = NodeAdministator
    extra = 1
class NodeAdmin(BaseNodeAdmin):
    inlines = (NodeAdministatorInline,)
    def get_modelcls(self):
        return Node


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

    def get_instances_where_admin(self, user):
        admnodes = NodeAdmin.get_admnodes(user)
        f = self.get_modelcls().objects.filter(id__in=admnodes)
        return f


class SubjectAdministatorInline(admin.TabularInline):
    model = SubjectAdministator
    extra = 1
class SubjectAdmin(BaseNodeAdmin):
    inlines = (SubjectAdministatorInline,)
    def get_modelcls(self):
        return Subject
    def get_instances_where_admin(self, user):
        admnodes = NodeAdmin.get_admnodes(user)
        return self.get_modelcls().objects.filter(
                Q(admins=user) | Q(parent__id__in=admnodes))


class PeriodAdministatorInline(admin.TabularInline):
    model = PeriodAdministator
    extra = 1
class PeriodAdmin(BaseNodeAdmin):
    list_display = ['subject', 'short_name', 'start_time', 'end_time', 'admins_unicode']
    search_fields = ['short_name', 'long_name', 'subject__short_name']
    list_filter = ['start_time', 'end_time']
    ordering = ['subject']
    inlines = (PeriodAdministatorInline,)
    def get_modelcls(self):
        return Period
    def get_instances_where_admin(self, user):
        admnodes = NodeAdmin.get_admnodes(user)
        return self.get_modelcls().objects.filter(
                Q(admins=user) |
                Q(subject__admins=user) |
                Q(subject__parent__id__in=admnodes))


class AssignmentAdministatorInline(admin.TabularInline):
    model = AssignmentAdministator
    extra = 1
class AssignmentAdmin(BaseNodeAdmin):
    inlines = (AssignmentAdministatorInline,)
    def get_modelcls(self):
        return Assignment
    def get_instances_where_admin(self, user):
        admnodes = NodeAdmin.get_admnodes(user)
        return self.get_modelcls().objects.filter(
                Q(admins=user) |
                Q(period__admins=user) |
                Q(period__subject__admins=user) |
                Q(period__subject__parent__id__in=admnodes))



class DeliveryStudentInline(admin.TabularInline):
    model = DeliveryStudent
    extra = 1
class DeliveryExaminerInline(admin.TabularInline):
    model = DeliveryExaminer
    extra = 1
class DeliveryAdmin(LimitAccess, admin.ModelAdmin):
    inlines = (DeliveryStudentInline, DeliveryExaminerInline)
    def get_modelcls(self):
        return Delivery
    def get_instances_where_admin(self, user):
        admnodes = NodeAdmin.get_admnodes(user)
        return self.get_modelcls().objects.filter(
                Q(assignment__admins=user) |
                Q(assignment__period__admins=user) |
                Q(assignment__period__subject__admins=user) |
                Q(assignment__period__subject__parent__id__in=admnodes))



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
