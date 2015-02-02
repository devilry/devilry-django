from django.contrib import admin

from . import models as detektormodels


class DetektorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'processing_started_datetime', 'processing_started_by', 'id']
    list_filter = ['processing_started_datetime']
    search_fields = [
        'id',
        'assignment__id',
        'assignment__short_name',
        'assignment__long_name',
        'assignment__parentnode__short_name',
        'assignment__parentnode__long_name',
        'assignment__parentnode__parentnode__short_name',
        'assignment__parentnode__parentnode__long_name',
    ]

    def get_queryset(self, request):
        return super(DetektorAssignmentAdmin, self).get_queryset(request)\
            .select_related('assignment')

admin.site.register(detektormodels.DetektorAssignment, DetektorAssignmentAdmin)


class DetektorDeliveryParseResultAdmin(admin.ModelAdmin):
    list_display = [
        'delivery',
        'detektorassignment',
        'language',
        'number_of_operators',
        'number_of_keywords',
    ]
    list_filter = [
        'language'
    ]
    search_fields = [
        'id',
        'delivery__id',
        'detektorassignment__assignment__id',
        'detektorassignment__assignment__short_name',
        'detektorassignment__assignment__long_name',
        'detektorassignment__assignment__parentnode__short_name',
        'detektorassignment__assignment__parentnode__long_name',
        'detektorassignment__assignment__parentnode__parentnode__short_name',
        'detektorassignment__assignment__parentnode__parentnode__long_name',
    ]

    def get_queryset(self, request):
        return super(DetektorDeliveryParseResultAdmin, self).get_queryset(request)\
            .select_related(
                'delivery',
                'detektorassignment',
                'detektorassignment__assignment',
                'detektorassignment__assignment__parentnode',
                'detektorassignment__assignment__parentnode__parentnode')

admin.site.register(detektormodels.DetektorDeliveryParseResult, DetektorDeliveryParseResultAdmin)
