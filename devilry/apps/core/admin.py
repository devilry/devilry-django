from django.contrib import admin
from devilry.apps.core.models import AssignmentGroup, Node, Subject, Period, Assignment
from django.utils.translation import ugettext_lazy as _


class BaseNodeAdmin(admin.ModelAdmin):
    filter_horizontal = ['admins']
    raw_id_fields = [
        'parentnode'
    ]
    list_display = (
        'id',
        'short_name',
        'long_name',
        'path_as_string',
        'admins_as_string'
    )
    search_fields = [
        'id',
        'short_name',
        'long_name',
        'admins__shortname',
        'admins__fullname',
    ]

    def admins_as_string(self, obj):
        return u', '.join([user.username for user in obj.admins.all()])

    admins_as_string.short_description = _("Admins")

    def path_as_string(self, obj):
        return obj.get_path()

    path_as_string.short_description = _("Path")

    def get_queryset(self, request):
        return super(BaseNodeAdmin, self).get_queryset(request) \
            .prefetch_related(
            'admins')


class NodeAdmin(BaseNodeAdmin):
    def get_queryset(self, request):
        return super(NodeAdmin, self).get_queryset(request) \
            .select_related('parentnode')


admin.site.register(Node, NodeAdmin)


class SubjectAdmin(BaseNodeAdmin):
    pass


admin.site.register(Subject, SubjectAdmin)


class PeriodAdmin(BaseNodeAdmin):
    pass


admin.site.register(Period, PeriodAdmin)


class AssignmentAdmin(BaseNodeAdmin):
    search_fields = BaseNodeAdmin.search_fields + [
        'parentnode__long_name',
        'parentnode__short_name',
        'parentnode__parentnode__long_name',
        'parentnode__parentnode__short_name',
    ]


admin.site.register(Assignment, AssignmentAdmin)


class AssignmentGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'long_displayname')
    search_fields = [
        'id',
    ]
    readonly_fields = [
        'parentnode',
        'feedback',
        'last_deadline'
    ]

    def get_queryset(self, request):
        return super(AssignmentGroupAdmin, self).get_queryset(request) \
            .select_related(
            'parentnode', 'parentnode__parentnode',
            'parentnode__parentnode__parentnode')

        # def admins_as_string(self, obj):
        #     return ', '.join([user.username for user in obj.admins.all()])
        # admins_as_string.short_description = "Admins"


admin.site.register(AssignmentGroup, AssignmentGroupAdmin)
