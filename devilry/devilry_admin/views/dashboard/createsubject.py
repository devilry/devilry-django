

from crispy_forms import layout
from django import forms
from django.utils.translation import gettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy import crinstance
from cradmin_legacy.viewhelpers import create
from cradmin_legacy.viewhelpers import crudbase

from devilry.apps.core.models import Subject


class CreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'long_name',
            'short_name',
        ]

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = gettext_lazy('Type the name of your course.')


class CreateUpdateMixin(object):
    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('long_name', placeholder=gettext_lazy('Example: DUCK1010 Object Oriented Programming'),
                             focusonme='focusonme'),
                layout.Field('short_name', placeholder=gettext_lazy('Example: duck1010')),
                css_class='cradmin-globalfields'
            )
        ]


class CreateView(crudbase.OnlySaveButtonMixin, CreateUpdateMixin, create.CreateView):
    form_class = CreateForm
    model = Subject
    template_name = 'devilry_cradmin/viewhelpers/devilry_createview_with_backlink.django.html'

    def get_pagetitle(self):
        return gettext_lazy('Create new course')

    def get_success_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin_subjectadmin',
            appname='overview',
            roleid=self.created_subject.id
        )

    def form_saved(self, object):
        self.created_subject = object

    def get_backlink_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin',
            appname='overview'
        )

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
