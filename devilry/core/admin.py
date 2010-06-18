from models import (Node, Subject, Period, Assignment,
        AssignmentGroup, Candidate, Delivery, FileMeta)
from django.contrib import admin
from django.db.models import Q
from django.db import models
from django import forms



class BaseNodeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'get_path', 'get_admins')
    search_fields = ['short_name', 'long_name', 'admins__username']


class NodeAdmin(BaseNodeAdmin):
    pass

class SubjectAdmin(BaseNodeAdmin):
    search_fields = BaseNodeAdmin.search_fields + ['parentnode__short_name']

class PeriodAdmin(BaseNodeAdmin):
    list_display = ['parentnode', 'short_name', 'get_path',
            'start_time', 'end_time', 'get_admins']
    search_fields = BaseNodeAdmin.search_fields + ['parentnode__short_name']
    list_filter = ['start_time', 'end_time']
    ordering = ['parentnode']


class CandidateInline(admin.TabularInline):
    model = Candidate

class FileMetaInline(admin.TabularInline):
    model = FileMeta
    extra = 1

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['short_name', 'long_name', 'get_path', 'grade_plugin',
            'publishing_time', 'deadline', 'get_admins']
    search_fields = ['short_name', 'long_name', 'parentnode__short_name',
            'parentnode__parentnode__short_name', 'admins__username']
    list_filter = ['publishing_time', 'deadline']

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'id']
    inlines = [FileMetaInline]

class AssignmentGroupAdmin(BaseNodeAdmin):
    list_display = ['get_students', 'get_examiners', 'id', 'parentnode']
    search_fields = [
            'students__username',
            'examiners__username',
            'parentnode__short_name',
            'parentnode__parentnode__short_name',
            'parentnode__parentnode__parentnode__short_name']
    ordering = ['parentnode']
    inlines = [CandidateInline]

admin.site.register(Node, NodeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentGroup, AssignmentGroupAdmin)
admin.site.register(Delivery, DeliveryAdmin)
