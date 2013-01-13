from django.views.generic import View
from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder

from devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin
from devilry_qualifiesforexam.pluginhelpers import BackButton, NextButton



class AllApprovedView(View, QualifiesForExamPluginViewMixin):
    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not feedback or not feedback.is_passing_grade:
                return False
        return True

    def get(self, request):
        return self.handle_save_results_and_redirect_to_preview_request()



class SubsetApprovedView(FormView, QualifiesForExamPluginViewMixin):
    template_name = 'devilry_qualifiesforexam_approved/subsetselect.django.html'

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

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for assignmentid, grouplist in aggregated_relstudentinfo.assignments.iteritems():
            if assignmentid in self.assignments_to_pass:
                feedback = grouplist.get_feedback_with_most_points()
                if not (feedback and feedback.is_passing_grade):
                    return False
        return True

    def form_valid(self, form):
        self.assignments_to_pass = set(map(int, form.cleaned_data['assignments']))
        self.save_plugin_output(self.get_relatedstudents_that_qualify_for_exam())
#        self.save_settings_in_session()
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