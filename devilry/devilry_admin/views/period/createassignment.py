from crispy_forms import layout
from django import forms
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
            'Type the name of your assignment. Devilry will automatically suggest a name '
            'for you if the name of the previous assignment ends with a number.')
        self.fields['short_name'].help_text = _(
            'Up to 20 letters of lowercase english letters (a-z), '
            'numbers, underscore ("_") and hyphen ("-").')
        self.fields['first_deadline'].widget = DateTimePickerWidget()
        self.fields['first_deadline'].required = True
        self.fields['first_deadline'].help_text = _(
            'The first deadline for this assignment. This is shared by all the '
            'students on the assignment. You can add individual deadlines '
            'to give single students/groups an extended deadline.'
        )
        # self.__init_studentsetup()


class CreateView(crudbase.OnlySaveButtonMixin, create.CreateView):
    form_class = CreateForm
    model = Assignment

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Div(
                    layout.Div(
                        layout.Field('long_name', placeholder=_('Example: Obligatory assignment 1'),
                                     css_class='input-lg'),
                        css_class='col-sm-7'
                    ),
                    layout.Div(
                        layout.Field('short_name', placeholder=_('Example: oblig1')),
                        css_class='col-sm-5'
                    ),
                    css_class='row'
                ),
                layout.Div(
                    layout.Div(
                        layout.Field('first_deadline'),
                        css_class='col-sm-7'
                    ),
                    layout.Div(
                        layout.Div(
                            layout.HTML('TODO: Suggested deadlines'),
                            css_class='form-group'
                        ),
                        css_class='col-sm-5'
                    ),
                    css_class='row'
                ),
                css_class='cradmin-globalfields'
            )
        ]


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
