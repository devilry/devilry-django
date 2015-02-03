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


class AssignmentGroupListView(studentobjecttable.StudentObjectTableView):
    model = AssignmentGroup
    columns = [
        LongNameColumn,
        # StatusColumn,
    ]

    def get_pagetitle(self):
        return _('Assignments')

    def get_queryset_for_role(self, period):
        return AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .select_related('parentnode', 'parentnode__parentnode', 'parentnode__parentnode__parentnode')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AssignmentGroupListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
