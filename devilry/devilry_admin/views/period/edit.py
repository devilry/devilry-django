from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import crudbase
from django_cradmin.viewhelpers import update

from devilry.apps.core.models import Period
from devilry.devilry_admin.views.subject import createperiod


class UpdateView(crudbase.OnlySaveButtonMixin, createperiod.CreateUpdateMixin,
                 update.UpdateRoleView):
    template_name = 'devilry_admin/period/edit/updateview.django.html'

    form_class = createperiod.CreateUpdateForm
    model = Period

    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def get_pagetitle(self):
        period = self.request.cradmin_role
        return ugettext_lazy('Edit %(period)s') % {
            'period': period.get_path()
        }

    def get_success_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()


class App(crapp.App):
    appurls = [
        crapp.Url(r'^',
                  UpdateView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
