

from django.utils.translation import gettext_lazy, pgettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_examiner.views.selfassign import utils as selfassign_utils


class AssignmentItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'assignment'

    def get_title(self):
        return '{} - {}'.format(self.assignment.parentnode.get_path(), self.assignment.long_name)

    def get_description(self):
        if self.assignment.waiting_for_feedback_count > 0:
            return gettext_lazy('%(waiting_for_feedback_count)s waiting for feedback') % {
                'waiting_for_feedback_count': self.assignment.waiting_for_feedback_count
            }
        else:
            return gettext_lazy('Nobody waiting for feedback')

    def get_extra_css_classes_list(self):
        css_classes = ['devilry-examiner-listbuilder-assignmentlist-assignmentitemvalue']
        if self.assignment.waiting_for_feedback_count > 0:
            css_classes.append('devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-warning')
        else:
            css_classes.append('devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-muted')
        return css_classes


class AssignmentItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'assignment'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_examiner_assignment',
            appname='grouplist',
            roleid=self.assignment.id,
            viewname=crapp.INDEXVIEW_NAME,
        )


class AssignmentListView(listbuilderview.FilterListMixin,
                         listbuilderview.View):
    model = coremodels.Assignment
    value_renderer_class = AssignmentItemValue
    frame_renderer_class = AssignmentItemFrame

    def get_filterlist_template_name(self):
        return 'devilry_examiner/dashboard/assignmentlist.django.html'

    def get_pagetitle(self):
        return pgettext_lazy('examiner assignmentlist',
                             'Examiner dashboard')

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label=gettext_lazy('Search'),
            label_is_screenreader_only=True,
            modelfields=[
                'long_name',
                'short_name',
                'parentnode__long_name',
                'parentnode__short_name',
                'parentnode__parentnode__long_name',
                'parentnode__parentnode__short_name',
            ]))
        filterlist.append(devilry_listfilter.assignment.OrderByDeliveryTime())
        filterlist.append(devilry_listfilter.assignment.AssignmentCheckboxFilter())

    def get_unfiltered_queryset_for_role(self, role):
        return coremodels.Assignment.objects \
            .filter_examiner_has_access(user=self.request.user) \
            .annotate_with_waiting_for_feedback_count() \
            .select_related('parentnode', 'parentnode__parentnode')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selfassign_available_periods'] = selfassign_utils.selfassign_available_periods(
            user=self.request.user
        )
        return context

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  AssignmentListView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  AssignmentListView.as_view(),
                  name='filter'),
    ]
