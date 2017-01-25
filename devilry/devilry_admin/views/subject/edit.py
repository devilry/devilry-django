from __future__ import unicode_literals

from crispy_forms import layout
from devilry.apps.core.models import Subject
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import crudbase
from django_cradmin.viewhelpers import update


class UpdateView(crudbase.OnlySaveButtonMixin, update.UpdateRoleView):
    template_name = 'devilry_admin/subject/edit/updateview.django.html'

    model = Subject

    fields = [
        'long_name',
        'short_name'
    ]

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('long_name', placeholder=ugettext_lazy('Example: DUCK1010 Object Oriented Programming'),
                             focusonme='focusonme'),
                layout.Field('short_name', placeholder=ugettext_lazy('Example: duck1010')),
                css_class='cradmin-globalfields'
            )
        ]

    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

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
