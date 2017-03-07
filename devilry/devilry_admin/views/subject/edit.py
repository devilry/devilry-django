from __future__ import unicode_literals

from crispy_forms import layout
from devilry.apps.core.models import Subject
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import crudbase
from django_cradmin.viewhelpers import update

from devilry.devilry_admin.views.dashboard import createsubject


class UpdateView(crudbase.OnlySaveButtonMixin,
                 createsubject.CreateUpdateMixin,
                 update.UpdateRoleView):
    template_name = 'devilry_admin/subject/edit/updateview.django.html'

    model = Subject

    fields = [
        'long_name',
        'short_name'
    ]

    def get_pagetitle(self):
        subject = self.request.cradmin_role
        return ugettext_lazy('Edit %(subject)s') % {
            'subject': subject.get_path()
        }

    def get_success_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()


class App(crapp.App):
    appurls = [
        crapp.Url(r'^',
                  UpdateView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
