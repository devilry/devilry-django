from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from django_cradmin import crinstance
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_student.cradminextensions import studentobjecttable


class LongNameColumn(objecttable.SingleActionColumn):
    modelfield = 'id'
    normalcells_css_classes = ['objecttable-cell-strong']

    def get_header(self):
        return _('Name')

    def render_value(self, group):
        return group.parentnode.long_name

    def get_actionurl(self, group):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='overview',
            roleid=group.id)

    def is_sortable(self):
        return False


# class LastDeadlineColumn(objecttable.DatetimeColumn):
#     orderingfield = 'last_deadline_datetime'
#     modelfield = 'last_deadline_datetime'
#
#     def get_header(self):
#         return _('Deadline')
#
#     def is_sortable(self):
#         return False


class StatusColumn(objecttable.Column):
    template_name = 'devilry_student/cradmin_period/assignmentsapp/statuscolumn.django.html'
    context_value_name = 'status'
    context_object_name = 'group'
    column_width = '250px'

    def get_header(self):
        return _('Status')

    def render_value(self, group):
        return group.get_status()


class AssignmentGroupListView(studentobjecttable.StudentObjectTableView):
    model = AssignmentGroup
    template_name = 'devilry_student/cradmin_period/assignmentsapp/assignmentgroup-list.django.html'
    columns = [
        LongNameColumn,
        # LastDeadlineColumn,
        StatusColumn,
    ]

    def get_context_data(self, **kwargs):
        context = super(AssignmentGroupListView, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context

    def get_queryset_for_role(self, period):
        return AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .annotate_with_last_deadline_datetime()\
            .extra(
                order_by=['-last_deadline_datetime']
            )\
            .select_related(
                'parentnode',  # Assignment
                'parentnode__parentnode',  # Period
                'parentnode__parentnode__parentnode'  # Subject
            )


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AssignmentGroupListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
