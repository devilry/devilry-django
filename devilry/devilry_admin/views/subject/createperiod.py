from __future__ import unicode_literals
from crispy_forms import layout
from django import forms
from django.db import models
from django_cradmin import crapp
from django_cradmin import crinstance
from django_cradmin.viewhelpers import create
from django_cradmin.viewhelpers import crudbase
from django.utils.translation import ugettext_lazy as _
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core.models import Period
from devilry.utils import nodenamesuggestor


class CreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = [
            'long_name',
            'short_name',
            'start_time',
            'end_time',
        ]

    def __init__(self, *args, **kwargs):
        super(CreateUpdateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = _('Type the name of your semester.')
        self.fields['start_time'].widget = DateTimePickerWidget(required=True)
        self.fields['end_time'].widget = DateTimePickerWidget(required=True)


class CreateForm(CreateUpdateForm):
    class Meta:
        model = Period
        fields = CreateUpdateForm.Meta.fields + [
            'parentnode'
        ]

    def __init__(self, *args, **kwargs):
        self.subject = kwargs.pop('subject')
        super(CreateForm, self).__init__(*args, **kwargs)

        # We ignore this, we just need to include it to be able to
        # change the value in clean()
        self.fields['parentnode'].widget = forms.HiddenInput()
        self.fields['parentnode'].required = False

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        cleaned_data['parentnode'] = self.subject
        return cleaned_data


class CreateUpdateMixin(object):
    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('long_name', placeholder=_('Example: Spring 2025'),
                             focusonme='focusonme'),
                layout.Field('short_name', placeholder=_('Example: spring2025')),
                layout.Div(
                    layout.Div(
                        layout.Field('start_time'),
                        css_class='col-sm-6'
                    ),
                    layout.Div(
                        layout.Field('end_time'),
                        css_class='col-sm-6'
                    ),
                    css_class='row'
                ),
                css_class='cradmin-globalfields'
            )
        ]


class CreateView(crudbase.OnlySaveButtonMixin, CreateUpdateMixin, create.CreateView):
    form_class = CreateForm
    model = Period

    def dispatch(self, *args, **kwargs):
        self.subject = self.request.cradmin_role
        self.previous_period = self.subject.periods \
            .order_by('end_time') \
            .last()
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_pagetitle(self):
        return u'{} - {}'.format(self.get_pageheading(), self.subject.short_name)

    def get_pageheading(self):
        return _('Create new semester')

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['subject'] = self.subject
        return kwargs

    def get_initial(self):
        initial = super(CreateView, self).get_initial()
        if self.previous_period:
            namesuggestion = nodenamesuggestor.Suggest(long_name=self.previous_period.long_name,
                                                       short_name=self.previous_period.short_name)
            if namesuggestion.has_suggestion():
                namecollision_queryset = self.subject.periods.filter(
                    models.Q(long_name=namesuggestion.suggested_long_name) |
                    models.Q(short_name=namesuggestion.suggested_short_name))
                if not namecollision_queryset.exists():
                    initial['long_name'] = namesuggestion.suggested_long_name
                    initial['short_name'] = namesuggestion.suggested_short_name
        return initial

    def get_success_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='overview',
            roleid=self.created_period.id
        )

    def form_saved(self, object):
        self.created_period = object


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
