from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_cradmin import crapp

from devilry.apps.core.models import Delivery
from devilry.devilry_student.cradminextensions.columntypes import NaturaltimeAndDateTimeColumn

from .recentdeliveriesapp import DeliverySummaryWithAssignmentColumn
from .recentdeliveriesapp import PeriodInfoColumn
from .recentdeliveriesapp import PeriodInfoXsColumn


class FeedbackSaveTimestampColumn(NaturaltimeAndDateTimeColumn):
    modelfield = 'save_timestamp'
    allcells_css_classes = ['hidden-xs']
    # orderingfield = 'last_feedback__save_timestamp'
    # column_width = '270px'

    def get_header(self):
        return _('Feedback time')

    def render_value(self, delivery):
        return super(FeedbackSaveTimestampColumn, self).render_value(delivery.last_feedback)

    def is_sortable(self):
        return False

    # def get_default_order_is_ascending(self):
    #     return False


class RecentDeliveriesListView(objecttable.ObjectTableView):
    model = Delivery
    context_object_name = 'deliveries'
    columns = [
        DeliverySummaryWithAssignmentColumn,
        PeriodInfoColumn,
        PeriodInfoXsColumn,
        FeedbackSaveTimestampColumn,
    ]

    def get_queryset_for_role(self, user):
        return Delivery.objects\
            .filter_is_candidate(user)\
            .exclude(last_feedback=None)\
            .select_related(
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode',
                'last_feedback')

    def get_pagetitle(self):
        return _('Recent feedbacks')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            RecentDeliveriesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
