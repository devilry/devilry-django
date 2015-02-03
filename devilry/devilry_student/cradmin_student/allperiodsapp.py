from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from django_cradmin import crinstance
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import AssignmentGroup, Period
from devilry.devilry_student.cradminextensions import studentobjecttable


class PeriodInfoColumn(objecttable.SingleActionColumn):
    """
    Period info column used for tablets and desktop devices.
    """
    modelfield = 'id'
    normalcells_css_classes = ['objecttable-cell-flat-paragraphs']
    template_name = 'devilry_student/cradmin_student/allperiodsapp/periodinfo-column.django.html'
    context_object_name = 'period'

    def get_orderby_args(self, order_ascending):
        if order_ascending:
            return ['parentnode__long_name', 'long_name']
        else:
            return ['-parentnode__long_name', '-long_name']

    def is_sortable(self):
        return True

    def get_context_data(self, obj):
        context = super(PeriodInfoColumn, self).get_context_data(obj=obj)
        context['is_active'] = obj.is_active()
        return context

    def get_default_order_is_ascending(self):
        return None

    def get_header(self):
        return _('Course')

    def render_value(self, period):
        return u'{} - {}'.format(
            period.subject.long_name,
            period.long_name)

    def get_actionurl(self, period):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_student_period',
            appname='assignments',
            roleid=period.id)


class AllPeriodsListView(studentobjecttable.StudentObjectTableView):
    model = AssignmentGroup
    template_name = 'devilry_student/cradmin_student/allperiodsapp/all-periods-list.django.html'
    columns = [
        PeriodInfoColumn,
    ]

    def get_queryset_for_role(self, period):
        return Period.objects\
            .filter_is_candidate_or_relatedstudent(user=self.request.user)\
            .annotate_with_user_qualifies_for_final_exam(user=self.request.user)\
            .select_related('parentnode')\
            .order_by('-start_time', 'parentnode__long_name')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AllPeriodsListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
