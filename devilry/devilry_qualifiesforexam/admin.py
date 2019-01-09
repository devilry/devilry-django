from django.contrib import admin
from devilry.devilry_qualifiesforexam.models import Status, QualifiesForFinalExam


class QualifiesForFinalExamInline(admin.TabularInline):
    model = QualifiesForFinalExam
    raw_id_fields = [
        'relatedstudent'
    ]
    fields = ['relatedstudent', 'qualifies']
    readonly_fields = ['relatedstudent', 'qualifies']
    extra = 0


class StatusAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'period'
    ]
    inlines = [QualifiesForFinalExamInline]
    list_display = (
        'id',
        'period',
        'get_status_text',
        'createtime',
        'message',
    )
    search_fields = [
        'id',
        'period__short_name',
        'period__long_name',
        'period__parentnode__short_name',
        'period__parentnode__long_name',
        'message',
    ]
    readonly_fields = [
        'period',
        'createtime',
        'message',
        'user',
        'plugin',
        'exported_timestamp',
        'status'
    ]

    def get_queryset(self, request):
        return super(StatusAdmin, self).get_queryset(request)\
            .select_related(
                'period', 'period__parentnode')

    # def admins_as_string(self, obj):
    #     return ', '.join([user.username for user in obj.admins.all()])
    # admins_as_string.short_description = "Admins"


admin.site.register(Status, StatusAdmin)


class QualifiesForFinalExamAdmin(admin.ModelAdmin):
    raw_id_fields = [
        'relatedstudent'
    ]
    list_display = (
        'id',
        'qualifies'
    )
    search_fields = [
        'id'
    ]



admin.site.register(QualifiesForFinalExam, QualifiesForFinalExamAdmin)
