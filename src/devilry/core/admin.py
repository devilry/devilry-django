from models import *
#from models import Node, Subject, Period, Assignment, \
        #Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin
from django.db.models import Q



class LimitAccess:
    def queryset(self, request):
        """ Limit administrators to superusers, and administators on this
        node or any of the parent-nodes. """
        if request.user.is_superuser:
            return self.get_modelcls().objects
        else:
            return self.get_instances_where_admin(request.user)

    def get_instances_where_admin(self, user):
        raise NotImplementedError()

    def get_modelcls(self):
        raise NotImplementedError()



class BaseNodeAdmin(LimitAccess, admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path')
    search_fields = ['short_name', 'long_name']


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
    list_display = ['subject', 'short_name', 'start_time', 'end_time']
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
        return self.get_modelcls().objects.filter(
                Q(assignment__admins=user) |
                Q(assignment__period__admins=user) |
                Q(assignment__period__subject__admins=user) |
                Q(assignment__period__subject__parent__admins=user))


admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)

admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DeliveryCandidate)
admin.site.register(FileMeta)
