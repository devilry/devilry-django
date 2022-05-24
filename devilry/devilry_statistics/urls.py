from django.urls import re_path

from devilry.devilry_statistics.api.assignment import examiner_average_grading_points, examiner_group_results, \
    examiner_details


urlpatterns = [
    re_path(r'^assignment/examiner-average-points/(?P<assignment_id>\d+)/(?P<relatedexaminer_id>\d+)$',
        examiner_average_grading_points.ExaminerAverageGradingPointsApi.as_view(),
        name='devilry_assignment_statistics_examiner_average_points'),
    re_path(r'^assignment/examiner-group-results/(?P<assignment_id>\d+)/(?P<relatedexaminer_id>\d+)$',
        examiner_group_results.ExaminerGroupResultApi.as_view(),
        name='devilry_assignment_statistics_examiner_group_results'),
    re_path(r'^assignment/examiner-details/(?P<assignment_id>\d+)/(?P<relatedexaminer_id>\d+)$',
        examiner_details.ExaminerDetailsApi.as_view(),
        name='devilry_assignment_statistics_examiner_details')
]
