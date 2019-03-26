from cradmin_legacy import crapp

from devilry.devilry_admin.views.assignment.passed_previous_period import overview
from devilry.devilry_admin.views.assignment.passed_previous_period import passed_previous_period
from devilry.devilry_admin.views.assignment.passed_previous_period import passed_previous_semester_manual


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            overview.Overview.as_view(),
            name=crapp.INDEXVIEW_NAME
        ),

        # Auto pass students on selected period.
        crapp.Url(
            r'^select-period$',
            passed_previous_period.SelectPeriodView.as_view(),
            name='select_period'),
        crapp.Url(
            r'^assignment/(?P<period_id>\d+)$',
            passed_previous_period.PassedPreviousAssignmentView.as_view(),
            name='assignments'),
        crapp.Url(
            r'^confirm/(?P<period_id>\d+)$',
            passed_previous_period.ApprovePreviousAssignments.as_view(),
            name='confirm'),

        # Manually select students to pass.
        crapp.Url(r'^select-groups/(?P<filters_string>.+)?$',
                  passed_previous_semester_manual.PassAssignmentGroupsView.as_view(),
                  name='manually_select_groups'),
    ]