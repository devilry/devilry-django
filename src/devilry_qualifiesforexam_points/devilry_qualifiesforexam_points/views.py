from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder

from devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin
from devilry_qualifiesforexam.pluginhelpers import BackButton, NextButton
from devilry_qualifiesforexam.models import Status
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
                settings = current_status.devilry_qualifiesforexam_approved_subsetpluginsetting
            except PointsPluginSetting.DoesNotExist:
                pass
            else:
                ids = [selected.assignment.id for selected in settings.selectedassignment_set.all()]
                return {'assignments': ids}
        ids = [assignment.id for assignment in self.period.assignments.all()]
        return {'assignments': ids}

    def get_form_class(self):
        choices = [(a.id, a.long_name) for a in self.period.assignments.order_by('publishing_time')]
        backurl = self.get_selectplugin_url()
        class SelectAssignmentForm(forms.Form):
            assignments = forms.MultipleChoiceField(
                required=True,
                label=_('Select assignments that students must pass to qualify for final exams'),
                widget=forms.CheckboxSelectMultiple,
                choices=choices)

            def __init__(self, *args, **kwargs):
                self.helper = FormHelper()
                self.helper.layout = Layout(
                    'assignments',
                    ButtonHolder(
                        BackButton(backurl),
                        NextButton()
                    )
                )
                super(SelectAssignmentForm, self).__init__(*args, **kwargs)

        return SelectAssignmentForm

    def form_valid(self, form):
        assignmentids_that_must_be_passed = set(map(int, form.cleaned_data['assignments']))
        qualified_relstudentids = PeriodResultsCollectorPoints(assignmentids_that_must_be_passed).get_relatedstudents_that_qualify_for_exam(self.period)
        self.save_plugin_output(qualified_relstudentids)
        self.save_settings_in_session({
            'assignmentids_that_must_be_passed': assignmentids_that_must_be_passed
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
