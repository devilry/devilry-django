from models import *
#from models import Node, Subject, Period, Assignment, \
        #Delivery, DeliveryCandidate, FileMeta
from django.contrib import admin
from django.db.models import Q




class BaseNodeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name')
    search_fields = ['short_name', 'long_name']

    def queryset(self, request):
        """ Limit administrators to superusers, and administators on this
        node or any of the parent-nodes. """
        if request.user.is_superuser:
            return self.get_modelcls().objects
        else:
            return self.get_admins(request)

    def get_admins(self, request):
        raise NotImplementedException()

    def get_modelcls(self):
        raise NotImplementedException()


class NodeAdmin(BaseNodeAdmin):
    def get_modelcls(self):
        return Node
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(admins=request.user)

class SubjectAdmin(BaseNodeAdmin):
    def get_modelcls(self):
        return Subject
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) | Q(parent__admins=request.user))

class PeriodAdmin(BaseNodeAdmin):
    def get_modelcls(self):
        return Period
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) |
                Q(parent__admins=request.user) |
                Q(parent__admins__admins=request.user))

class AssignmentAdmin(BaseNodeAdmin):
    def get_modelcls(self):
        return Assignment
    def get_admins(self, request):
        return self.get_modelcls().objects.filter(
                Q(admins=request.user) |
                Q(parent__admins=request.user) |
                Q(parent__admins__admins=request.user) |
                Q(parent__admins__admins__admins=request.user))


class NodeAdministatorAdmin(admin.ModelAdmin):
    list_display = ('node', 'user')
    search_fields = ['node__name', 'user__username']
    list_filter = ['user']


admin.site.register(Node, NodeAdmin)
admin.site.register(NodeAdministator, NodeAdministatorAdmin)

admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectAdministator, NodeAdministatorAdmin)

admin.site.register(Period)
admin.site.register(PeriodAdministator, NodeAdministatorAdmin)

admin.site.register(Assignment)
admin.site.register(AssignmentAdministator, NodeAdministatorAdmin)

admin.site.register(Delivery)
admin.site.register(DeliveryCandidate)
admin.site.register(FileMeta)
