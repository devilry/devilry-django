from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers.listbuilder.itemframe import DefaultSpacingItemFrame
from django_cradmin.viewhelpers.listbuilder.lists import RowList

from devilry.apps.core.models import RelatedExaminer, AssignmentGroup
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listfilter.utils import WithResultValueRenderable


class ExaminerDetailPageLinkFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'relatedexaminer'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='examinerdetails',
            roleid=self.kwargs['assignment'].id,
            viewname=crapp.INDEXVIEW_NAME,
            kwargs={'relatedexaminer_id': self.relatedexaminer.id}
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-assignment-students-overview-group-linkframe']


class StudentGroupListMatchResultRenderable(WithResultValueRenderable):
    def get_object_name_singular(self, num_matches):
        return ugettext_lazy('examiner')

    def get_object_name_plural(self, num_matches):
        return ugettext_lazy('examiners')


class RowListWithMatchResults(RowList):
    def append_results_renderable(self):
        result_info_renderable = StudentGroupListMatchResultRenderable(
            value=None,
            num_matches=self.num_matches,
            num_total=self.num_total
        )
        self.renderable_list.insert(0, DefaultSpacingItemFrame(inneritem=result_info_renderable))

    def __init__(self, num_matches, num_total, page):
        self.num_matches = num_matches
        self.num_total = num_total
        self.page = page
        super(RowListWithMatchResults, self).__init__()

        if page == 1:
            self.append_results_renderable()


class Overview(listbuilder_relatedexaminer.ListViewBase):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/examiners/overview.django.html'
    listbuilder_class = RowListWithMatchResults
    value_renderer_class = listbuilder_relatedexaminer.OnassignmentItemValue
    frame_renderer_class = ExaminerDetailPageLinkFrame
    model = RelatedExaminer
    paginate_by = 20

    def get_period(self):
        return self.assignment.parentnode

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and devilryrole != 'departmentadmin':
            raise Http404(ugettext_lazy('Only department admins have permission to edit examiners '
                                        'for fully anonymous assignments.'))
        return super(Overview, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            self.filterview_name,
            kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        assignment = role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .annotate_with_number_of_groups_on_assignment(assignment=assignment) \
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=assignment)\
            .exclude(active=False)

        # Set unfiltered count on self.
        self.num_total = queryset.count()
        return queryset

    def get_queryset_for_role(self, role):
        queryset = super(Overview, self).get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset

    def get_listbuilder_list_kwargs(self):
        kwargs = super(Overview, self).get_listbuilder_list_kwargs()
        kwargs['num_matches'] = self.num_matches or 0
        kwargs['num_total'] = self.num_total or 0
        kwargs['page'] = self.request.GET.get('page', 1)
        return kwargs

    def get_value_and_frame_renderer_kwargs(self):
        kwargs = super(Overview, self).get_value_and_frame_renderer_kwargs()
        assignment = self.request.cradmin_role
        kwargs['assignment'] = assignment
        return kwargs

    def get_assignment_groups_without_any_examiners(self):
        return AssignmentGroup.objects\
            .filter(parentnode=self.request.cradmin_role, examiners__isnull=True)

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignment'] = self.assignment
        context['examiner_count'] = RelatedExaminer.objects\
            .filter(period=self.request.cradmin_role.period)\
            .exclude(active=False)\
            .count()
        context['students_without_examiners_exists'] = self.get_assignment_groups_without_any_examiners().exists()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
