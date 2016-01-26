from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer


class RelatedExaminerItemValue(listbuilder_relatedexaminer.ReadOnlyItemValue):
    pass


class Overview(listbuilder_relatedexaminer.ListViewBase):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/examiners/overview.django.html'
    value_renderer_class = RelatedExaminerItemValue
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
        return RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')

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
