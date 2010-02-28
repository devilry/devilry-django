from models import (Node, Subject, Period, Assignment,
        AssignmentGroup, Delivery, FileMeta)
from django.contrib import admin
from django.db.models import Q
from django.db import models
from django import forms
from devilry.auth import authadmin



class BaseNodeAdmin(authadmin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path')
    search_fields = ['short_name', 'long_name']


class NodeAdmin(BaseNodeAdmin):

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


class SubjectAdmin(BaseNodeAdmin):
    pass


class PeriodAdmin(BaseNodeAdmin):
    list_display = ['parentnode', 'short_name', 'start_time', 'end_time', 'admins_unicode']
    search_fields = ['short_name', 'long_name', 'parentnode__short_name']
    list_filter = ['start_time', 'end_time']
    ordering = ['parentnode']


class AssignmentAdmin(BaseNodeAdmin):
    pass

class DeliveryGroupAdmin(authadmin.ModelAdmin):
    pass



class FileMetaInline(admin.TabularInline):
    model = FileMeta
    extra = 1
class DeliveryAdmin(authadmin.ModelAdmin):
    list_display = ['__unicode__', 'id']
    inlines = (FileMetaInline,)


admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)

admin.site.register(AssignmentGroup, DeliveryGroupAdmin)
admin.site.register(Delivery, DeliveryAdmin)
