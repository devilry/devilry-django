from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer
from devilry.devilry_cradmin import devilry_listbuilder


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


class Overview(listbuilder_relatedexaminer.ListViewBase):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/examiners/overview.django.html'
    value_renderer_class = listbuilder_relatedexaminer.OnassignmentItemValue
    frame_renderer_class = ExaminerDetailPageLinkFrame
    model = RelatedExaminer

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
            .annotate_with_number_of_groups_on_assignment(assignment=assignment)\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=assignment)\
            .exclude(active=False)
        return queryset

    def get_value_and_frame_renderer_kwargs(self):
        kwargs = super(Overview, self).get_value_and_frame_renderer_kwargs()
        assignment = self.request.cradmin_role
        kwargs['assignment'] = assignment
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignment'] = self.assignment
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
