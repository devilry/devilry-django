from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from extjs4.views import Extjs4AppView

from devilry.devilry_qualifiesforexam.pluginhelpers import QualifiesForExamPluginViewMixin


class BaseAppView(Extjs4AppView):
    template_name = "devilry_qualifiesforexam_select/app.django.html"
    appname = 'devilry_qualifiesforexam_select'
    title = _('Select students that qualifies for final exams - Devilry')


class QualifiesBasedOnManualSelectView(BaseAppView, QualifiesForExamPluginViewMixin):
    pluginid = 'devilry_qualifiesforexam_select'

    def get_context_data(self, **kwargs):
        context = super(QualifiesBasedOnManualSelectView, self).get_context_data(**kwargs)
        context['backurl'] = self.get_selectplugin_url()
        return context

    def post(self, request):
        try:
            self.get_plugin_input_and_authenticate()  # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()

        qualified_relstudentids = request.POST.getlist('qualified_relstudentids', [])
        if not isinstance(qualified_relstudentids, list):
            return HttpResponseBadRequest('``qualified_relstudentids`` must be a list/array.')
        try:
            qualified_relstudentids = set(map(int, qualified_relstudentids))
        except ValueError:
            return HttpResponseBadRequest('All items in ``qualified_relstudentids`` must be integers.')

        self.save_plugin_output(qualified_relstudentids)
        return self.redirect_to_preview_url()

    def get(self, request):
        try:
            self.get_plugin_input_and_authenticate()  # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        return super(QualifiesBasedOnManualSelectView, self).get(request)


class BuildExtjsAppView(BaseAppView):
    pass
