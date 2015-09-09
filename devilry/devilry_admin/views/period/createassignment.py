from datetime import timedelta
from crispy_forms import layout
from django import forms
from django.template.loader import render_to_string
from django_cradmin import crapp
from django_cradmin.viewhelpers import create
from django_cradmin.viewhelpers import crudbase
from django.utils.translation import ugettext_lazy as _
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget
from devilry.apps.core.models import Assignment


class CreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'long_name',
            'short_name',
            'first_deadline',
        ]

    # studentsetup = forms.ChoiceField(
    #     required=True,
    #     label=_('How would you like to setup students and examiners?'))
    #
    # def __init_studentsetup(self):
    #     choices = []
    #     if self.period.assignments.count() > 0:
    #         help_text = _('Choose the option that is closest to your preferences. You can '
    #                       're-organize students and examiners after the assignment is '
    #                       'created.')
    #     else:
    #         help_text = _('Choose the option that is closest to your preferences. '
    #                       'If you have the same '
    #                       'You can '
    #                       're-organize students and examiners after the assignment is '
    #                       'created.')
    #
    #     self.fields['studentsetup'].choices = choices
    #     self.fields['studentsetup'].help_text = help_text

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
        # self.__init_studentsetup()


class CreateView(crudbase.OnlySaveButtonMixin, create.CreateView):
    form_class = CreateForm
    model = Assignment
    suggested_deadlines_template_name = 'devilry_admin/period/createassignment/suggested_deadlines.django.html'
    helpbox_template_name = 'devilry_admin/period/createassignment/helpbox.django.html'

    def __get_suggested_deadlines(self):
        suggested_deadlines = []
        period = self.request.cradmin_role
        last_assignment = period.assignments\
            .exclude(first_deadline=None)\
            .order_by('first_deadline')\
            .last()
        if last_assignment and last_assignment.first_deadline:
            for days_forward in range(7, (7*4)+1, 7):
                print(days_forward)
                suggested_deadline = last_assignment.first_deadline + timedelta(days=days_forward)
                suggested_deadlines.append(suggested_deadline)
        return suggested_deadlines

    def __render_suggested_deadlines_box(self):
        return render_to_string(self.suggested_deadlines_template_name, {
            'suggested_deadlines': self.__get_suggested_deadlines()
        })

    def __render_help_box(self):
        return render_to_string(self.helpbox_template_name)

    def get_form_css_classes(self):
        return super(CreateView, self).get_form_css_classes() + ['django-cradmin-form-fullwidth']

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Div(
                    layout.Div(
                        layout.Field('long_name', placeholder=_('Example: Obligatory assignment 1'),
                                     focusonme='focusonme'),
                        layout.Field('short_name', placeholder=_('Example: oblig1')),
                        css_class='col-sm-7'
                    ),
                    layout.Div(
                        layout.HTML(self.__render_help_box()),
                        css_class='col-sm-5'
                    ),
                    css_class='row'
                ),
                # layout.HTML('<hr>'),
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
