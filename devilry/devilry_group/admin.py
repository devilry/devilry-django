from django.contrib import admin
from devilry.devilry_group import models


class FeedbackSetAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.FeedbackSet, FeedbackSetAdmin)


class GroupCommentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'part_of_grading'
    ]

    raw_id_fields = [
        'feedback_set'
    ]


admin.site.register(models.GroupComment, GroupCommentAdmin)


class FeedbackSetPassedPreviousPeriodAdmin(admin.ModelAdmin):
    readonly_fields = [
        'feedbackset',
        'passed_previous_period_type',
        'assignment_short_name',
        'assignment_long_name',
        'assignment_max_points',
        'assignment_passing_grade_min_points',
        'period_short_name',
        'period_long_name',
        'period_start_time',
        'period_end_time',
        'grading_points',
        'grading_published_by',
        'grading_published_datetime',
        'created_datetime',
        'created_by',
    ]
    search_fields = [
        'feedbackset_id',
        'created_by_id',
        'passed_previous_period_type'
    ]
    list_display = [
        'feedbackset'
    ]


admin.site.register(models.FeedbacksetPassedPreviousPeriod, FeedbackSetPassedPreviousPeriodAdmin)


class FeedbackSetGradingUpdateHistoryAdmin(admin.ModelAdmin):
    readonly_fields = [
        'feedback_set',
        'updated_by',
        'updated_datetime',
        'old_grading_points',
        'old_grading_published_by',
        'old_grading_published_datetime'
    ]
    search_fields = [
        'feedbackset_id',
        'updated_by_id',
        'old_grading_published_by_id'
    ]
    list_display = [
        'feedback_set',
        'updated_by'
    ]


admin.site.register(models.FeedbackSetGradingUpdateHistory, FeedbackSetGradingUpdateHistoryAdmin)


class FeedbackSetDeadlineHistoryAdmin(admin.ModelAdmin):
    readonly_fields = [
        'feedback_set',
        'changed_by',
        'changed_datetime',
        'deadline_old',
        'deadline_new'
    ]
    search_fields = [
        'feedback_set_id',
        'changed_by_id'
    ]
    list_display = [
        'feedback_set',
        'changed_datetime'
    ]


admin.site.register(models.FeedbackSetDeadlineHistory, FeedbackSetDeadlineHistoryAdmin)


class GroupCommentEditHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'visibility',
        'edited_datetime',
        'edited_by'
    ]


admin.site.register(models.GroupCommentEditHistory, GroupCommentEditHistoryAdmin)
