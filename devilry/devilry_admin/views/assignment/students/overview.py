# -*- coding: utf-8 -*-


from django.utils.translation import gettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers.listbuilder.itemframe import DefaultSpacingItemFrame
from cradmin_legacy.viewhelpers.listbuilder.lists import RowList

from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listfilter.utils import WithResultValueRenderable


class NonAnonymousGroupItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_admin',
            roleid=self.group.id,
            appname='feedbackfeed'
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-assignment-students-overview-group-linkframe']


class StudentGroupListMatchResultRenderable(WithResultValueRenderable):
    def get_object_name_singular(self, num_matches):
        return gettext_lazy('group')

    def get_object_name_plural(self, num_matches):
        return gettext_lazy('groups')


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


class Overview(groupview_base.BaseInfoView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/overview.django.html'
    listbuilder_class = RowListWithMatchResults

    def get_frame_renderer_class(self):
        devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and devilryrole != 'departmentadmin':
            return None
        else:
            return NonAnonymousGroupItemFrame

    #
    # Add support for showing results on the top of the list.
    #
    def get_listbuilder_list_kwargs(self):
        kwargs = super(Overview, self).get_listbuilder_list_kwargs()
        kwargs['num_matches'] = self.num_matches or 0
        kwargs['num_total'] = self.num_total or 0
        kwargs['page'] = self.request.GET.get('page', 1)
        return kwargs

    def get_unfiltered_queryset_for_role(self, role):
        queryset = super(Overview, self).get_unfiltered_queryset_for_role(role=role)

        # Set unfiltered count on self.
        self.num_total = queryset.count()
        return queryset

    def get_queryset_for_role(self, role):
        queryset = super(Overview, self).get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
