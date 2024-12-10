

from django.utils.translation import pgettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter

from devilry.apps.core.models import Assignment, RelatedStudent, RelatedExaminer
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class AssignmentItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'assignment'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='overview',
            roleid=self.assignment.id,
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-period-overview-assignmentitemframe']


class Overview(listbuilderview.FilterListMixin, listbuilderview.View):
    template_name = 'devilry_admin/period/overview.django.html'
    model = Assignment
    frame_renderer_class = AssignmentItemFrame
    value_renderer_class = devilry_listbuilder.assignment.ItemValue
    paginate_by = 5

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            modelfields=[
                'long_name',
                'short_name',
            ],
            label_is_screenreader_only=True
        ))
        filterlist.append(devilry_listfilter.assignment.OrderBy())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        period = self.request.cradmin_role
        return Assignment.objects.filter(parentnode=period)\
            .filter_user_is_admin(user=self.request.user)\
            .order_by('-first_deadline', '-publishing_time')

    def __get_relatedstudent_count(self):
        period = self.request.cradmin_role
        return RelatedStudent.objects\
            .filter(period=period)\
            .count()

    def __get_relatedexaminer_count(self):
        period = self.request.cradmin_role
        return RelatedExaminer.objects \
            .filter(period=period)\
            .count()

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['relatedstudent_count'] = self.__get_relatedstudent_count()
        context['relatedexaminer_count'] = self.__get_relatedexaminer_count()
        context['period_admin_access_restricted'] = self.request.cradmin_instance\
            .period_admin_access_semi_anonymous_assignments_restricted()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
