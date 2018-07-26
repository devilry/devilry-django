from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy

from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listbuilder import user
from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import filters


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


class UserListView(listbuilderview.FilterListMixin, listbuilderview.View):
    template_name = 'devilry_admin/dashboard/student_feedbackfeed_wizard/student_feedbackfeed_list_users.django.html'
    model = get_user_model()
    frame_renderer_class = UserItemFrame
    filterview_name = 'user_filter'
    value_renderer_class = user.ItemValue
    paginate_by = 35

    def get_pagetitle(self):
        return ugettext_lazy('Select a student')

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            self.filterview_name,
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(filters.UserSearchExtension())

    def get_unfiltered_queryset_for_role(self, role):
        return get_user_model().objects.all().order_by('username')
