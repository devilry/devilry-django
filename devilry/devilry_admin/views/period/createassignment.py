from datetime import timedelta
import re
from crispy_forms import layout
from django import forms
from django.template.loader import render_to_string
from django_cradmin import crapp
from django_cradmin.viewhelpers import create
from django_cradmin.viewhelpers import crudbase
from django.utils.translation import ugettext_lazy as _
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget
from devilry.apps.core.models import Assignment


def create_suggested_name(name):
    match = re.match(r'^.+?(?P<suffixnumber>\d+)$', name)
    if match:
        suffixnumber = int(match.group(1))
        prefix = name[:match.start(1)]
        suggested_name = u'{}{}'.format(prefix, suffixnumber + 1)
        return suggested_name
    else:
        return ''


class CreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'long_name',
            'short_name',
            'first_deadline',
        ]

    def __init__(self, *args, **kwargs):
        # self.period = kwargs.pop('period')
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = _(
            'Type the name of your assignment.')
        self.fields['short_name'].help_text = _(
            'Up to 20 letters of lowercase english letters (a-z), '
            'numbers, underscore ("_") and hyphen ("-").')
        self.fields['first_deadline'].widget = DateTimePickerWidget()
        self.fields['first_deadline'].required = True
        self.fields['first_deadline'].label = _('Set first deadline')
        self.fields['first_deadline'].help_text = _(
            'The first deadline for this assignment. This is shared by all the '
            'students on the assignment.'
        )


class CreateView(crudbase.OnlySaveButtonMixin, create.CreateView):
    form_class = CreateForm
    model = Assignment
    suggested_deadlines_template_name = 'devilry_admin/period/createassignment/suggested_deadlines.django.html'
    helpbox_template_name = 'devilry_admin/period/createassignment/helpbox.django.html'

    def dispatch(self, *args, **kwargs):
        period = self.request.cradmin_role
        self.previous_assignment = period.assignments\
            .exclude(first_deadline=None)\
            .order_by('first_deadline')\
            .last()
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(CreateView, self).get_initial()
        if self.previous_assignment:
            initial['long_name'] = create_suggested_name(self.previous_assignment.long_name)
            initial['short_name'] = create_suggested_name(self.previous_assignment.short_name)
        return initial

    def __get_suggested_deadlines(self):
        suggested_deadlines = []
        if self.previous_assignment:
            for days_forward in range(7, (7*4)+1, 7):
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

    def get_form_helper(self):
        return


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
