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
            return self.get_admins(request)

    def get_admins(self, request):
        raise NotImplementedError()

    def get_modelcls(self):
        raise NotImplementedError()



class BaseNodeAdmin(admin.ModelAdmin, LimitAccess):
    list_display = ('short_name', 'long_name', 'get_path')
    search_fields = ['short_name', 'long_name']


class NodeAdministatorInline(admin.TabularInline):
    model = NodeAdministator
    extra = 1
class NodeAdmin(BaseNodeAdmin):
    inlines = (NodeAdministatorInline,)
    def get_modelcls(self):
        return Node
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(admins=request.user)


class SubjectAdministatorInline(admin.TabularInline):
    model = SubjectAdministator
    extra = 1
class SubjectAdmin(BaseNodeAdmin):
    inlines = (SubjectAdministatorInline,)
    def get_modelcls(self):
        return Subject
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) | Q(parent__admins=request.user))


class PeriodAdministatorInline(admin.TabularInline):
    model = PeriodAdministator
    extra = 1
class PeriodAdmin(BaseNodeAdmin):
    inlines = (PeriodAdministatorInline,)
    def get_modelcls(self):
        return Period
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) |
                Q(parent__admins=request.user) |
                Q(parent__admins__admins=request.user))


class AssignmentAdministatorInline(admin.TabularInline):
    model = AssignmentAdministator
    extra = 1
class AssignmentAdmin(BaseNodeAdmin):
    inlines = (AssignmentAdministatorInline,)
    def get_modelcls(self):
        return Assignment
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) |
                Q(parent__admins=request.user) |
                Q(parent__admins__admins=request.user) |
                Q(parent__admins__admins__admins=request.user))



class DeliveryStudentInline(admin.TabularInline):
    model = DeliveryStudent
    extra = 1
class DeliveryExaminerInline(admin.TabularInline):
    model = DeliveryExaminer
    extra = 1
class DeliveryAdmin(admin.ModelAdmin, LimitAccess):
    inlines = (DeliveryStudentInline, DeliveryExaminerInline)


admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)

admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(DeliveryCandidate)
admin.site.register(FileMeta)
