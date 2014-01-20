from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface


class PointsPluginApi(GradingSystemPluginInterface):
    id = 'devilry_gradingsystemplugin_points'
    title = _('Specify a number of points in an input field')
    description = _('Provides a form with a single field where a number of points is specified. The lowest possible number is zero, and you specify the maximum number of points allowed for this assignment.')

    def get_edit_feedback_url(self, deliveryid):
        return reverse('devilry_gradingsystemplugin_points_feedbackeditor', kwargs={'deliveryid': deliveryid})

    def get_bulkedit_feedback_url(self, assignmentid):
        return reverse('devilry_gradingsystemplugin_points_feedbackbulkeditor', kwargs={'assignmentid': assignmentid})

gradingsystempluginregistry.add(PointsPluginApi)
