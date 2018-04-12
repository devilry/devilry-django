from django_cradmin import crapp

from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import student_list, assignment_list

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  student_list.UserListView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^user-filter/(?P<filters_string>.+)?$',
                  student_list.UserListView.as_view(),
                  name='user_filter'),
        crapp.Url(r'^groups/(?P<user_id>\d+)?$',
                  assignment_list.StudentAssignmentGroupListView.as_view(),
                  name='student_groups'),
        crapp.Url(r'^groups/(?P<user_id>\d+)?/group-filter/(?P<filters_string>.+)?$',
                  assignment_list.StudentAssignmentGroupListView.as_view(),
                  name='student_group_filter'),
    ]