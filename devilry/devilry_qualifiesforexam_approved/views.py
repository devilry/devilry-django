from django.views.generic import View
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
from .post_statussave import PeriodResultsCollectorSubset
from .post_statussave import PeriodResultsCollectorAll
from .models import SubsetPluginSetting



class AllApprovedView(View, QualifiesForExamPluginViewMixin):
    pluginid = 'devilry_qualifiesforexam_approved.all'

    def get(self, request):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        qualified_relstudentids = PeriodResultsCollectorAll().get_relatedstudents_that_qualify_for_exam(self.period)
        self.save_plugin_output(qualified_relstudentids)
        return self.redirect_to_preview_url()



class SubsetApprovedView(FormView, QualifiesForExamPluginViewMixin):
    template_name = 'devilry_qualifiesforexam_approved/subsetselect.django.html'
    pluginid = 'devilry_qualifiesforexam_approved.subset'

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        try:
            current_status = Status.get_current_status(self.period)
        except Status.DoesNotExist:
            return {}
        else:
            try:
                settings = current_status.devilry_qualifiesforexam_approved_subsetpluginsetting
            except SubsetPluginSetting.DoesNotExist:
                return {}
            else:
                ids = [selected.assignment.id for selected in settings.selectedassignment_set.all()]
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
        qualified_relstudentids = PeriodResultsCollectorSubset(assignmentids_that_must_be_passed).get_relatedstudents_that_qualify_for_exam(self.period)
        self.save_plugin_output(qualified_relstudentids)
        self.save_settings_in_session({
            'assignmentids_that_must_be_passed': list(assignmentids_that_must_be_passed)
        })
        return self.redirect_to_preview_url()

    def post(self, request):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        return super(SubsetApprovedView, self).post(request)

    def get(self, request):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        return super(SubsetApprovedView, self).get(request)
