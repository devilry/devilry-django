from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse

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

    def _get_passing_students(self):
        passing_relatedstudents = []
        return passing_relatedstudents

    def get(self, request):
        self.read_querystring_parameters() # set self.periodid and self.pluginsessionid
        passing_relatedstudents = self._get_passing_students()
        self.save_results_for_preview(passing_relatedstudents)
        return super(AllApprovedView, self).get(request)

    def get_redirect_url(self, **kwargs):
        return reverse('devilry_qualifiesforexam_ui', kwargs={'periodid': self.periodid})
