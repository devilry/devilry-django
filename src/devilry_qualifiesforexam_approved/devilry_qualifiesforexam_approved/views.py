from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment

from devilry.apps.core.models import Period


# TODO: Auth



class QualifiesForExamViewMixin(object):
    def read_querystring_parameters(self):
        """
        Reads the parameters (periodid and pluginsessionid) from
        the querystring and store them as instance variables.
        """
        self.periodid = self.request.GET['periodid']
        self.period = get_object_or_404(Period, pk=self.periodid)
        self.pluginsessionid = self.request.GET['pluginsessionid']

    def save_results_for_preview(self, passing_relatedstudents):
        self.request.session[self.pluginsessionid] = {
            'relateduserids': [relatedstudent.id for relatedstudent in passing_relatedstudents]
        }



class AllApprovedView(RedirectView, QualifiesForExamViewMixin):
    permanent = False
    query_string = True

    def _passed_all_assignments(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not (feedback and feedback.is_passing_grade):
                return False
        return True

    def _get_passing_students(self):
        passing_relatedstudents = []
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.period)
        for aggregated_relstudentinfo in grouper.iter_relatedstudents_with_results():
            if self._passed_all_assignments(aggregated_relstudentinfo):
                passing_relatedstudents.append(aggregated_relstudentinfo.user)
        return passing_relatedstudents

    def get(self, request):
        self.read_querystring_parameters() # set self.periodid and self.pluginsessionid
        passing_relatedstudents = self._get_passing_students()
        self.save_results_for_preview(passing_relatedstudents)
        return super(AllApprovedView, self).get(request)

    def get_redirect_url(self, **kwargs):
        return reverse('devilry_qualifiesforexam_ui', kwargs={'periodid': self.periodid})
