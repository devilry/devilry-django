from __future__ import unicode_literals

import json

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import pgettext_lazy, ugettext_lazy, pgettext
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import PointToGradeMap


class GradingConfigurationForm(forms.Form):
    error_messages = {
        'point_to_grade_map_json_invalid_format': ugettext_lazy(
            'The grade to points table must have at least 2 rows. The first row must '
            'have 0 as points.'
        ),
        'max_points_too_small_for_point_to_grade_map': ugettext_lazy(
            'The grade to points table has points that is larger than the '
            'maximum number of points.'
        ),
        'max_points_larger_than_passing_grade_min_points': ugettext_lazy(
            'Must be larger than the minimum number of points required to pass.'
        )
    }

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
        help_text='...'
    )

    point_to_grade_map_json = forms.CharField(
        required=False,
        # widget=forms.TextInput()
        widget=forms.HiddenInput()
    )

    def __sort_point_to_grade_map(self, point_to_grade_map):
        return list(sorted(point_to_grade_map, key=lambda item: item[0]))

    def get_point_to_grade_map(self):
        return self.__sort_point_to_grade_map(
            json.loads(self.cleaned_data['point_to_grade_map_json']))

    def clean(self):
        cleaned_data = super(GradingConfigurationForm, self).clean()
        passing_grade_min_points = cleaned_data.get('passing_grade_min_points', None)
        max_points = cleaned_data.get('max_points', None)
        points_to_grade_mapper = cleaned_data.get('points_to_grade_mapper')
        point_to_grade_map_json = cleaned_data.get('point_to_grade_map_json', '').strip()
        point_to_grade_map = None
        if points_to_grade_mapper and points_to_grade_mapper == Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE:
            if not point_to_grade_map_json:
                raise ValidationError(self.error_messages['point_to_grade_map_json_invalid_format'])
            point_to_grade_map = self.__sort_point_to_grade_map(json.loads(point_to_grade_map_json))
            if len(point_to_grade_map) < 2:
                raise ValidationError(self.error_messages['point_to_grade_map_json_invalid_format'])
        if passing_grade_min_points is not None and max_points is not None:
            if passing_grade_min_points > max_points:
                raise ValidationError({
                    'max_points': self.error_messages['max_points_larger_than_passing_grade_min_points']
                })
        if max_points is not None and point_to_grade_map:
            largest_point_in_map = point_to_grade_map[-1][0]
            if largest_point_in_map > max_points:
                raise ValidationError({
                    'max_points': self.error_messages['max_points_too_small_for_point_to_grade_map']
                })


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
                'points_to_grade_mapper',
                layout.HTML(self._render_custom_table_div()),
                'point_to_grade_map_json',
                'passing_grade_min_points',
                'max_points',
                css_class='cradmin-globalfields')
        ]

    @property
    def assignment(self):
        if not hasattr(self, '_assignment'):
            queryset = Assignment.objects\
                .filter(id=self.request.cradmin_role.id)\
                .prefetch_point_to_grade_map()
            self._assignment = queryset.get()
        return self._assignment

    def get_initial(self):
        initial = {
            'grading_system_plugin_id': self.assignment.grading_system_plugin_id,
            'points_to_grade_mapper': self.assignment.points_to_grade_mapper,
            'passing_grade_min_points': self.assignment.passing_grade_min_points,
            'max_points': self.assignment.max_points,
        }
        if self.assignment.prefetched_point_to_grade_map is not None:
            initial['point_to_grade_map_json'] = json.dumps(
                self.assignment.prefetched_point_to_grade_map.as_choices())
        return initial

    def get_buttons(self):
        return [
            PrimarySubmit('save', ugettext_lazy('Save')),
        ]

    def __create_point_to_grade_map(self, form, assignment):
        PointToGradeMap.objects.filter(assignment=assignment).delete()
        if form.cleaned_data['points_to_grade_mapper'] != Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE:
            return
        point_to_grade_map = PointToGradeMap.objects.create(
            assignment=assignment, invalid=False)
        point_to_grade_map.create_map(*form.get_point_to_grade_map())
        point_to_grade_map.full_clean()

    def form_valid(self, form):
        assignment = self.request.cradmin_role
        assignment.grading_system_plugin_id = form.cleaned_data['grading_system_plugin_id']
        assignment.points_to_grade_mapper = form.cleaned_data['points_to_grade_mapper']
        assignment.passing_grade_min_points = form.cleaned_data['passing_grade_min_points']
        assignment.max_points = form.cleaned_data['max_points']
        assignment.full_clean()
        with transaction.atomic():
            assignment.save()
            self.__create_point_to_grade_map(form=form, assignment=assignment)
            messages.success(
                request=self.request,
                message=ugettext_lazy('Saved Grading configuration for assignment')
            )
        return super(AssignmentGradingConfigurationUpdateView, self).form_valid(form)

    def get_backlink_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def get_context_data(self, **kwargs):
        context = super(AssignmentGradingConfigurationUpdateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context
