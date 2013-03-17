#from django.views.generic import View
#from django.http import HttpResponseForbidden
#from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from extjs4.views import Extjs4AppView

#from devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin
#from devilry_qualifiesforexam.models import Status
#from .post_statussave import PeriodResultsCollectorPoints





#class QualifiesBasedOnManualSelectView(View, QualifiesForExamPluginViewMixin):
    #pluginid = 'devilry_qualifiesforexam_select'

    #def form_valid(self, form):
        #assignmentids = set(map(int, form.cleaned_data['assignments']))
        #minimum_points = form.cleaned_data['minimum_points']
        #collector = PeriodResultsCollectorPoints(assignmentids, minimum_points)
        #qualified_relstudentids = collector.get_relatedstudents_that_qualify_for_exam(self.period)
        #self.save_plugin_output(qualified_relstudentids)
        #self.save_settings_in_session({
            #'assignmentids': assignmentids,
            #'minimum_points': minimum_points
        #})
        #return self.redirect_to_preview_url()

    #def post(self, request):
        #try:
            #self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        #except PermissionDenied:
            #return HttpResponseForbidden()
        #return super(QualifiesBasedOnPointsView, self).post(request)

    #def get(self, request):
        #try:
            #self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        #except PermissionDenied:
            #return HttpResponseForbidden()
        #return super(QualifiesBasedOnPointsView, self).get(request)






class QualifiesBasedOnManualSelectView(Extjs4AppView):
    template_name = "devilry_qualifiesforexam_select/app.django.html"
    appname = 'devilry_qualifiesforexam_select'
    title = _('Select students that qualifies for final exams - Devilry')
