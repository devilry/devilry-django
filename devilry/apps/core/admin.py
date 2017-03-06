from django.contrib import admin
from devilry.apps.core.models import AssignmentGroup, Node, Subject, Period, Assignment, PeriodTag
from django.utils.translation import ugettext_lazy as _


class BaseNodeAdmin(admin.ModelAdmin):
    filter_horizontal = ['admins']
    raw_id_fields = [
        'parentnode',
    ]

    # Added between id,name and admins in :meth:`.get_list_display`.
    list_display_middle = []

    # Added to search_fields in :meth:`.get_search_fields`.
    extra_search_fields = []

    def get_search_fields(self, request):
        return [
            'id',
            'short_name',
            'long_name',
            'admins__shortname',
            'admins__fullname',
        ] + self.extra_search_fields

    def get_list_display(self, request):
        return [
            'id',
            'short_name',
            'long_name',
        ] + self.list_display_middle + [
            'admins_as_string',
        ]

    def admins_as_string(self, obj):
        return u', '.join([user.shortname for user in obj.admins.all()])

    admins_as_string.short_description = _("Admins")

    def get_queryset(self, request):
        return super(BaseNodeAdmin, self).get_queryset(request) \
            .prefetch_related('admins')


class NodeAdmin(BaseNodeAdmin):
    list_display_middle = ['path_as_string']

    def path_as_string(self, obj):
        return obj.get_path()
    path_as_string.short_description = _("Path")

    def get_queryset(self, request):
        return super(NodeAdmin, self).get_queryset(request) \
            .select_related('parentnode')


admin.site.register(Node, NodeAdmin)


class SubjectAdmin(BaseNodeAdmin):
    pass


admin.site.register(Subject, SubjectAdmin)


class PeriodAdmin(BaseNodeAdmin):
    extra_search_fields = [
        'parentnode__long_name',
        'parentnode__short_name',
    ]
    list_display_middle = [
        'get_subject',
        'start_time',
        'end_time',
    ]
    list_filter = [
        'start_time',
        'end_time',
    ]

    def get_subject(self, obj):
        return obj.subject.short_name
    get_subject.short_description = _('Subject')
    get_subject.admin_order_field = 'parentnode__short_name'


admin.site.register(Period, PeriodAdmin)


class AssignmentAdmin(BaseNodeAdmin):
    extra_search_fields = [
        'parentnode__long_name',
        'parentnode__short_name',
        'parentnode__parentnode__long_name',
        'parentnode__parentnode__short_name',
    ]
    list_display_middle = [
        'get_subject',
        'get_period',
        'publishing_time',
        'first_deadline',
    ]
    list_filter = [
        'anonymizationmode',
        'publishing_time',
        'first_deadline',
    ]

    def get_subject(self, obj):
        return obj.subject.short_name
    get_subject.short_description = _('Subject')
    get_subject.admin_order_field = 'parentnode__parentnode__short_name'

    def get_period(self, obj):
        return obj.period.short_name
    get_period.short_description = _('Period')
    get_period.admin_order_field = 'parentnode__short_name'


admin.site.register(Assignment, AssignmentAdmin)


class AssignmentGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_subject',
        'get_period',
        'get_assignment',
        'short_displayname',
        'created_datetime',
    ]
    search_fields = [
        'id',
        'parentnode__long_name',
        'parentnode__short_name',
        'parentnode__parentnode__long_name',
        'parentnode__parentnode__short_name',
        'parentnode__parentnode__parentnode__long_name',
        'parentnode__parentnode__parentnode__short_name',
    ]
    readonly_fields = [
        'parentnode',
        'feedback',
    ]
    list_filter = [
        'created_datetime',
    ]

    def get_subject(self, obj):
        return obj.subject.short_name
    get_subject.short_description = _('Subject')
    get_subject.admin_order_field = 'parentnode__parentnode__parentnode__short_name'

    def get_period(self, obj):
        return obj.period.short_name
    get_period.short_description = _('Period')
    get_period.admin_order_field = 'parentnode__parentnode__short_name'

    def get_assignment(self, obj):
        return obj.assignment.short_name
    get_assignment.short_description = _('Assignment')
    get_assignment.admin_order_field = 'parentnode__short_name'

    def get_queryset(self, request):
        return super(AssignmentGroupAdmin, self).get_queryset(request) \
            .select_related('parentnode',
                            'parentnode__parentnode',
                            'parentnode__parentnode__parentnode')\


admin.site.register(AssignmentGroup, AssignmentGroupAdmin)


class PeriodTagAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prefix',
        'tag',
        'is_hidden',
    ]

    filter_horizontal = [
        'relatedstudents',
        'relatedexaminers',
    ]

admin.site.register(PeriodTag, PeriodTagAdmin)
