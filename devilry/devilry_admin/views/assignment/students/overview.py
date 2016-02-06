from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class NonAnonymousGroupItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='groupdetails',
            roleid=self.kwargs['assignment'].id,
            viewname='groupdetails',
            kwargs={'pk': self.group.id}
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-assignment-students-overview-group-linkframe']


class Overview(groupview_base.BaseInfoView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/overview.django.html'

    def get_frame_renderer_class(self):
        devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and devilryrole != 'departmentadmin':
            return None
        else:
            return NonAnonymousGroupItemFrame


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
