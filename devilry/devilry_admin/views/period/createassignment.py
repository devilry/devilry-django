from datetime import timedelta
import re

from crispy_forms import layout
from django import forms
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django_cradmin import crapp
from django_cradmin.viewhelpers import create
from django_cradmin.viewhelpers import crudbase
from django.utils.translation import ugettext_lazy as _
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core.models import Assignment


class NameSuggestion(object):
    pattern = re.compile(r'^.+?(?P<suffixnumber>\d+)$')

    def __init__(self, long_name, short_name):
        self.long_name = long_name
        self.short_name = short_name
        self.number = self.__find_common_number()
        self.suggested_short_name = ''
        self.suggested_long_name = ''
        if self.number is not None:
            self.__suggest_names_from_number()

    def has_suggestion(self):
        return self.number is not None

    def __extract_number(self, name):
        match = self.pattern.match(name)
        if match:
            return int(match.group(1))
        else:
            return None

    def __find_common_number(self):
        """
        If both short and long name is suffixed with the same number,
        return the number as an int. If not, return ``None``.
        """
        short_name_number = self.__extract_number(self.short_name)
        if short_name_number is None:
            return None
        long_name_number = self.__extract_number(self.long_name)
        if long_name_number is None:
            return None
        if short_name_number == long_name_number:
            return short_name_number
        else:
            return None

    def __suggest_name_from_number(self, name):
        match = self.pattern.match(name)
        prefix = name[:match.start(1)]
        suggested_name = u'{}{}'.format(prefix, self.number + 1)
        return suggested_name

    def __suggest_names_from_number(self):
        self.suggested_long_name = self.__suggest_name_from_number(self.long_name)
        self.suggested_short_name = self.__suggest_name_from_number(self.short_name)


class CreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'long_name',
            'short_name',
            'first_deadline',
            'publishing_time',
            'parentnode'
        ]

    def __init__(self, *args, **kwargs):
        self.period = kwargs.pop('period')
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = _(
            'Type the name of your assignment.')
        self.fields['short_name'].help_text = _(
            'Up to 20 letters of lowercase english letters (a-z), '
            'numbers, underscore ("_") and hyphen ("-").')
        self.fields['first_deadline'].widget = DateTimePickerWidget(required=True)
        self.fields['first_deadline'].required = True
        self.fields['first_deadline'].label = _('Set first deadline')
        self.fields['first_deadline'].help_text = _(
            'The first deadline for this assignment. This is shared by all the '
            'students on the assignment.'
        )

        # We ignore this, we just need to include it to be able to
        # change the value in clean()
        self.fields['publishing_time'].widget = forms.HiddenInput()
        self.fields['publishing_time'].required = False

        # We ignore this, we just need to include it to be able to
        # change the value in clean()
        self.fields['parentnode'].widget = forms.HiddenInput()
        self.fields['parentnode'].required = False

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        first_deadline = cleaned_data.get('first_deadline', None)
        cleaned_data['parentnode'] = self.period
        if first_deadline:
            publishing_time = timezone.now() + timedelta(
                minutes=settings.DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES)
            cleaned_data['publishing_time'] = publishing_time
        return cleaned_data


class CreateView(crudbase.OnlySaveButtonMixin, create.CreateView):
    form_class = CreateForm
    model = Assignment
    suggested_deadlines_template_name = 'devilry_admin/period/createassignment/suggested_deadlines.django.html'
    helpbox_template_name = 'devilry_admin/period/createassignment/helpbox.django.html'

    def dispatch(self, *args, **kwargs):
        self.period = self.request.cradmin_role
        self.previous_assignment = self.period.assignments \
            .exclude(first_deadline=None) \
            .order_by('first_deadline') \
            .last()
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['period'] = self.request.cradmin_role
        return kwargs

    def get_initial(self):
        initial = super(CreateView, self).get_initial()
        if self.previous_assignment:
            namesuggestion = NameSuggestion(long_name=self.previous_assignment.long_name,
                                            short_name=self.previous_assignment.short_name)
            if namesuggestion.has_suggestion():
                namecollision_queryset = self.period.assignments.filter(
                    models.Q(long_name=namesuggestion.suggested_long_name) |
                    models.Q(short_name=namesuggestion.suggested_short_name))
                if not namecollision_queryset.exists():
                    initial['long_name'] = namesuggestion.suggested_long_name
                    initial['short_name'] = namesuggestion.suggested_short_name
        return initial

    def __get_suggested_deadlines(self):
        suggested_deadlines = []
        if self.previous_assignment:
            for days_forward in range(7, (7 * 4) + 1, 7):
                suggested_deadline = self.previous_assignment.first_deadline + timedelta(days=days_forward)
                suggested_deadlines.append(suggested_deadline)
        return suggested_deadlines

    def __render_suggested_deadlines_box(self):
        return render_to_string(self.suggested_deadlines_template_name, {
            'suggested_deadlines': self.__get_suggested_deadlines()
        })

    def __render_help_box(self):
        return render_to_string(self.helpbox_template_name)

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Div(
                    layout.Div(
                        layout.HTML(self.__render_help_box()),
                        css_class='col-sm-5 col-sm-push-7'
                    ),
                    layout.Div(
                        layout.Field('long_name', placeholder=_('Example: Obligatory assignment 1'),
                                     focusonme='focusonme'),
                        layout.Field('short_name', placeholder=_('Example: oblig1')),
                        css_class='col-sm-7 col-sm-pull-5'
                    ),
                    css_class='row'
                ),
                layout.Div(
                    layout.Div(
                        layout.Field('first_deadline'),
                        css_class='col-sm-6'
                    ),
                    layout.HTML(self.__render_suggested_deadlines_box()),
                    css_class='row'
                ),
                css_class='cradmin-globalfields'
            )
        ]


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
