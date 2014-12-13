from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder

from devilry.devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin
from devilry.devilry_qualifiesforexam.pluginhelpers import BackButton, NextButton
from devilry.devilry_qualifiesforexam.models import Status
from .post_statussave import PeriodResultsCollectorPoints
from .models import PointsPluginSetting





class QualifiesBasedOnPointsView(FormView, QualifiesForExamPluginViewMixin):
    template_name = 'devilry_qualifiesforexam_points/subsetselect.django.html'
    pluginid = 'devilry_qualifiesforexam_points'

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        try:
            current_status = Status.get_current_status(self.period)
        except Status.DoesNotExist:
            pass
        else:
            try:
                settings = current_status.devilry_qualifiesforexam_points_pointspluginsetting
            except PointsPluginSetting.DoesNotExist:
                pass
            else:
                ids = [selected.assignment.id for selected in settings.pointspluginselectedassignment_set.all()]
                return {'assignments': ids}
        ids = [assignment.id for assignment in self.period.assignments.all()]
        return {'assignments': ids}

    def get_form_class(self):
        choices = [(a.id, a.long_name) for a in self.period.assignments.order_by('publishing_time')]
        backurl = self.get_selectplugin_url()
        class SelectAssignmentForm(forms.Form):
            assignments = forms.MultipleChoiceField(
                required=True,
                label=_('Assignments to include when counting points'),
                widget=forms.CheckboxSelectMultiple,
                choices=choices)
            minimum_points = forms.IntegerField(
                    required=True,
                    min_value=0,
                    label=_('Minimum number of points required in total on the selected assignments'))

            def __init__(self, *args, **kwargs):
                self.helper = FormHelper()
                self.helper.layout = Layout(
                    'assignments',
                    'minimum_points',
                    ButtonHolder(
                        BackButton(backurl),
                        NextButton()
                    )
                )
                super(SelectAssignmentForm, self).__init__(*args, **kwargs)

        return SelectAssignmentForm

    def form_valid(self, form):
        assignmentids = set(map(int, form.cleaned_data['assignments']))
        minimum_points = form.cleaned_data['minimum_points']
        collector = PeriodResultsCollectorPoints(assignmentids, minimum_points)
        qualified_relstudentids = collector.get_relatedstudents_that_qualify_for_exam(self.period)
        self.save_plugin_output(qualified_relstudentids)
        self.save_settings_in_session({
            'assignmentids': list(assignmentids),
            'minimum_points': minimum_points
        })
        return self.redirect_to_preview_url()

    def post(self, request):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        return super(QualifiesBasedOnPointsView, self).post(request)

    def get(self, request):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        return super(QualifiesBasedOnPointsView, self).get(request)
