from django.views.generic import RedirectView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden

from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment
from devilry_qualifiesforexam.pluginhelpers import QualifiesForExamViewMixin



class PluginView(RedirectView, QualifiesForExamViewMixin):
    permanent = False
    query_string = True

    def passed_period(self, aggregated_relstudentinfo):
        raise NotImplementedError()

    def get_passing_students(self):
        passing_relatedstudentsids = []
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.period)
        for aggregated_relstudentinfo in grouper.iter_relatedstudents_with_results():
            if self.passed_period(aggregated_relstudentinfo):
                passing_relatedstudentsids.append(aggregated_relstudentinfo.relatedstudent.id)
        return passing_relatedstudentsids

    def handle_request(self):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        self.save_plugin_output(self.get_passing_students())
        return RedirectView.get(self, self.request)

    def get_redirect_url(self, **kwargs):
        return self.get_preview_url()


class AllApprovedView(PluginView):
    def passed_period(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not (feedback and feedback.is_passing_grade):
                return False
        return True

    def get(self, request):
        return self.handle_request()
#
#
#class SubsetApprovedView(PluginView):
#    def passed_period(self, aggregated_relstudentinfo):
#        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
#            feedback = grouplist.get_feedback_with_most_points()
#            if not (feedback and feedback.is_passing_grade):
#                return False
#        return True
#
#    def post(self, request):
#        return self.handle_request()