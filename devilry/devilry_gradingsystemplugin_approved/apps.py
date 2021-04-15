from django.apps import AppConfig
from django.utils.translation import gettext_lazy
from django.urls import reverse

from devilry.devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface


class ApprovedPluginApi(GradingSystemPluginInterface):
    id = 'devilry_gradingsystemplugin_approved'
    sets_passing_grade_min_points_automatically = True
    sets_max_points_automatically = True
    title = gettext_lazy('Passed/failed')
    description = gettext_lazy('Provides a single checkbox that can be checked to provide a passing grade.')

    def get_edit_feedback_url(self, deliveryid):
        return reverse('devilry_gradingsystemplugin_approved_feedbackeditor', kwargs={'deliveryid': deliveryid})

    def get_passing_grade_min_points(self):
        return 1

    def get_max_points(self):
        return 1

    def get_bulkedit_feedback_url(self, assignmentid):
        return reverse('devilry_gradingsystemplugin_approved_feedbackbulkeditor', kwargs={'assignmentid': assignmentid})


class GradingsystemApprovedAppConfig(AppConfig):
    name = 'devilry.devilry_gradingsystemplugin_approved'

    def ready(self):
        gradingsystempluginregistry.add(ApprovedPluginApi)
