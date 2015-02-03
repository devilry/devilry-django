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


class StatusColumn(objecttable.Column):
    template_name = 'devilry_student/cradmin_period/assignmentsapp/statuscolumn.django.html'
    context_value_name = 'status'
    context_object_name = 'group'
    column_width = '200px'

    def get_header(self):
        return _('Status')

    def render_value(self, group):
        return group.get_status()


class AssignmentGroupListView(studentobjecttable.StudentObjectTableView):
    model = AssignmentGroup
    columns = [
        LongNameColumn,
        StatusColumn,
    ]

    def get_pagetitle(self):
        return _('Assignments')

    def get_queryset_for_role(self, period):
        return AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .annotate_with_number_of_deliveries()\
            .select_related(
                'parentnode',  # Assignment
                'parentnode__parentnode',  # Period
                'parentnode__parentnode__parentnode')  # Subject


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AssignmentGroupListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
