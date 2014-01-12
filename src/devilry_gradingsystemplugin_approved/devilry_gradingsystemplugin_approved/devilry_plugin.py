from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface


class ApprovedPluginApi(GradingSystemPluginInterface):
    id = 'devilry_gradingsystemplugin_approved'
    sets_passing_grade_min_points_automatically = True
    sets_max_points_automatically = True
    title = _('Specify approved or not approved delivery attempt')
    description = _('Provide a single checkbox which conclude the attempt to be approved when checked')

    def get_edit_feedback_url(self, deliveryid):
        return reverse('devilry_gradingsystemplugin_approved_feedbackeditor', kwargs={'deliveryid': deliveryid})

    def get_passing_grade_min_points(self):
        return 1

    def get_max_points(self):
        return 1


gradingsystempluginregistry.add(ApprovedPluginApi)
