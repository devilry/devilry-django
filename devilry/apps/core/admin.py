from django.contrib import admin
from devilry.apps.core.models import AssignmentGroup, Node, Subject, StaticFeedbackFileAttachment
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
        'admins_as_string'
    )
    search_fields = [
        'id',
        'short_name',
        'long_name',
        'admins__username',
        'admins__email',
        'admins__devilryuserprofile__full_name',
    ]

    def admins_as_string(self, obj):
        return u', '.join([user.username for user in obj.admins.all()])
    admins_as_string.short_description = _("Admins")

    def admins_as_string(self, obj):
        return obj.get_path()
    admins_as_string.short_description = _("Path")

    def get_queryset(self, request):
        return super(BaseNodeAdmin, self).get_queryset(request)\
            .prefetch_related(
                'admins',
                'admins__devilryuserprofile')


class NodeAdmin(BaseNodeAdmin):
    def get_queryset(self, request):
        return super(NodeAdmin, self).get_queryset(request)\
            .select_related('parentnode')\


admin.site.register(Node, NodeAdmin)


class SubjectAdmin(BaseNodeAdmin):
    pass

admin.site.register(Subject, SubjectAdmin)


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
        return super(AssignmentGroupAdmin, self).get_queryset(request)\
            .select_related(
                'parentnode', 'parentnode__parentnode',
                'parentnode__parentnode__parentnode')

    # def admins_as_string(self, obj):
    #     return ', '.join([user.username for user in obj.admins.all()])
    # admins_as_string.short_description = "Admins"

admin.site.register(AssignmentGroup, AssignmentGroupAdmin)


class StaticFeedbackFileAttachmentAdmin(admin.ModelAdmin):
    search_fields = [
        'id'
    ]

admin.site.register(StaticFeedbackFileAttachment, StaticFeedbackFileAttachmentAdmin)
