from django.views.generic import View

from devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin



class AllApprovedView(View, QualifiesForExamPluginViewMixin):
    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not feedback or not feedback.is_passing_grade:
                return False
        return True

    def get(self, request):
        return self.handle_save_results_and_redirect_to_preview_request()



class SubsetApprovedView(View, QualifiesForExamPluginViewMixin):
    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not (feedback and feedback.is_passing_grade):
                return False
        return True

    def post(self, request):
        return self.handle_save_results_and_redirect_to_preview_request()