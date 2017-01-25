from __future__ import unicode_literals

import json

from crispy_forms import layout
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import pgettext_lazy, ugettext_lazy, pgettext
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin

from devilry.apps.core.models import Assignment


class GradingConfigurationForm(forms.Form):
    grading_system_plugin_id = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(),
        choices=Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES,
        label=pgettext_lazy(
            'assignment config', 'Examiner chooses')
    )
    points_to_grade_mapper = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(),
        choices=Assignment.POINTS_TO_GRADE_MAPPER_CHOICES,
        label=pgettext_lazy(
            'assignment config', 'Students see')
    )
    passing_grade_min_points = forms.IntegerField(
        required=True,
        min_value=0,
        label=pgettext_lazy(
            'assignment config',
            'Minimum number of points required to pass')
    )

    max_points = forms.IntegerField(
        min_value=0,
        required=True,
        label='...',
        help_text='...',
        # help_text=pgettext_lazy(
        #     'assignment config',
        #     'The maximum number of points possible for this assignment.')
    )


class AssignmentGradingConfigurationUpdateView(OnlySaveButtonMixin, formbase.FormView):
    form_class = GradingConfigurationForm
    template_name = 'devilry_admin/assignment/gradingconfiguration-update/' \
                    'gradingconfiguration-update.django.html'
    extra_form_css_classes = ['django-cradmin-form-noasterisk']
    form_attributes = {
        'data-ievv-jsbase-widget': 'devilry-grading-configuration',
        'data-ievv-jsbase-widget-config': json.dumps({
            Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED: {
                'max_points_label': pgettext(
                    'assignment config',
                    'Points awarded for passing grade'),
            },
            Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS: {
                'max_points_label': pgettext(
                    'assignment config',
                    'Maximum number of points'),
                'max_points_help_text': pgettext(
                    'assignment config',
                    'The maximum number of points possible for this assignment.'),
            },
        })
    }

    def get_pagetitle(self):
        return pgettext_lazy('assignment config',
                             'Edit grading configuration')

    def _render_custom_table_div(self):
        return render_to_string(
            'devilry_admin/assignment/gradingconfiguration-update/custom-table.django.html',
            context={},
            request=self.request)

    def get_field_layout(self):
        return [
            layout.Div(
                'grading_system_plugin_id',
                'passing_grade_min_points',
                'max_points',
                'points_to_grade_mapper',
                layout.HTML(self._render_custom_table_div()),
                css_class='cradmin-globalfields')
        ]

    def get_initial(self):
        assignment = self.request.cradmin_role
        return {
            'grading_system_plugin_id': assignment.grading_system_plugin_id,
            'points_to_grade_mapper': assignment.points_to_grade_mapper,
            'passing_grade_min_points': assignment.passing_grade_min_points,
            'max_points': assignment.max_points,
        }

    def get_buttons(self):
        return [
            PrimarySubmit('save', ugettext_lazy('Save')),
        ]

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)
