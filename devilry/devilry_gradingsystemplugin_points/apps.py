from django.apps import AppConfig
from django.utils.translation import gettext_lazy
from django.urls import reverse

from devilry.devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface


class PointsPluginApi(GradingSystemPluginInterface):
    id = 'devilry_gradingsystemplugin_points'
    title = gettext_lazy('Points')
    description = gettext_lazy('Choose a number between zero and a maximum that you specify on the next page.')

    def get_edit_feedback_url(self, deliveryid):
        return reverse('devilry_gradingsystemplugin_points_feedbackeditor', kwargs={'deliveryid': deliveryid})

    def get_bulkedit_feedback_url(self, assignmentid):
        return reverse('devilry_gradingsystemplugin_points_feedbackbulkeditor', kwargs={'assignmentid': assignmentid})


class GradingsystemPointsAppConfig(AppConfig):
    name = 'devilry.devilry_gradingsystemplugin_points'

    def ready(self):
        gradingsystempluginregistry.add(PointsPluginApi)
