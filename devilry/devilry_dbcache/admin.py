from django.contrib import admin

from devilry.devilry_dbcache.models import AssignmentGroupCachedData


@admin.register(AssignmentGroupCachedData)
class AssignmentGroupCachedDataAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'group',
        'first_feedbackset',
        'last_feedbackset',
        'last_published_feedbackset',
        'new_attempt_count',
        'public_total_comment_count',
        'public_student_comment_count',
        'public_examiner_comment_count',
        'public_admin_comment_count',
        'public_student_file_upload_count',
        'examiner_count',
        'candidate_count'
    ]
    search_fields = [
        'id',
        'group__id',
        'group__parentnode__id',
        'group__parentnode__short_name',
        'group__parentnode__long_name',
        'group__parentnode__parentnode__id',
        'group__parentnode__parentnode__short_name',
        'group__parentnode__parentnode__long_name',
        'group__parentnode__parentnode__parentnode__id',
        'group__parentnode__parentnode__parentnode__short_name',
        'group__parentnode__parentnode__parentnode__long_name',
        'group__candidates__relatedstudent__candidate_id',
        'group__candidates__relatedstudent__candidate_id',
        'group__candidates__relatedstudent__user__shortname',
        'group__candidates__relatedstudent__user__fullname',
        'group__examiners__relatedexaminer__user__shortname',
        'group__examiners__relatedexaminer__user__fullname',
    ]
