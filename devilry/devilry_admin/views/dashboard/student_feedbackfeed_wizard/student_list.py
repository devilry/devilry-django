# -*- coding: utf-8 -*-


from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy

from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers.listbuilder.lists import RowList
from cradmin_legacy.viewhelpers.listbuilder.itemframe import DefaultSpacingItemFrame

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listbuilder import user
from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import filters
from devilry.devilry_cradmin.devilry_listfilter.utils import WithResultValueRenderable


class UserItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'user'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin',
            appname='studentfeedbackfeedwizard',
            viewname='student_groups',
            kwargs={
                'user_id': self.user.id
            }
        )


class StudentUserListMatchResultRenderable(WithResultValueRenderable):
    def get_object_name_singular(self, num_matches):
        return gettext_lazy('student')

    def get_object_name_plural(self, num_matches):
        return gettext_lazy('students')


class RowListWithMatchResults(RowList):
    def append_results_renderable(self):
        result_info_renderable = StudentUserListMatchResultRenderable(
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


class UserListView(listbuilderview.FilterListMixin, listbuilderview.View):
    template_name = 'devilry_admin/dashboard/student_feedbackfeed_wizard/student_feedbackfeed_list_users.django.html'
    model = get_user_model()
    listbuilder_class = RowListWithMatchResults
    frame_renderer_class = UserItemFrame
    filterview_name = 'user_filter'
    value_renderer_class = user.ItemValue
    paginate_by = 35

    def get_pagetitle(self):
        return gettext_lazy('Select a student')

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            self.filterview_name,
            kwargs={'filters_string': filters_string})

    #
    # Add support for showing results on the top of list.
    #
    def get_listbuilder_list_kwargs(self):
        kwargs = super(UserListView, self).get_listbuilder_list_kwargs()
        kwargs['num_matches'] = self.num_matches or 0
        kwargs['num_total'] = self.num_total or 0
        kwargs['page'] = self.request.GET.get('page', 1)
        return kwargs

    def add_filterlist_items(self, filterlist):
        filterlist.append(filters.UserSearchExtension())

    def get_unfiltered_queryset_for_role(self, role):
        relatedstudent_ids = RelatedStudent.objects.all()\
            .values_list('user_id', flat=True)
        queryset = get_user_model().objects\
            .filter(id__in=relatedstudent_ids)\
            .order_by('username')

        # Set unfiltered count on self.
        self.num_total = queryset.count()
        return queryset

    def get_queryset_for_role(self, role):
        queryset = super(UserListView, self).get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset
