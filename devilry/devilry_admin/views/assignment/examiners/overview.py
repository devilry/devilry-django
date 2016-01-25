from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer


class RelatedExaminerItemValue(listbuilder_relatedexaminer.ReadOnlyItemValue):
    pass


class Overview(listbuilderview.FilterListMixin, listbuilderview.View):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/examiners/overview.django.html'
    value_renderer_class = RelatedExaminerItemValue
    model = RelatedExaminer

    def get_queryset_for_role(self, role):
        assignment = role
        period = assignment.period
        return RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
