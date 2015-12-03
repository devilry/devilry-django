from django.apps import AppConfig
from django.utils.translation import ugettext_lazy

from devilry.devilry_qualifiesforexam import registry
from devilry.devilry_qualifiesforexam_approved.views import all_approved
from devilry.devilry_qualifiesforexam_approved.views import subset_approved


class AllApprovedPluginItem(registry.RegistryItem):
    id = 'devilry_qualifiesforexam_approved.all'

    def get_title(self):
        return ugettext_lazy('Students must pass ALL assignments')

    def get_description(self):
        return ugettext_lazy('Choose this option if you require your students to get a '
                             'passing grade on all their assignments to qualify '
                             'for final exams.')

    def get_viewclass(self):
        return all_approved.AllApprovedView


class SubsetApprovedPluginItem(registry.RegistryItem):
    id = 'devilry_qualifiesforexam_approved.subset'

    def get_title(self):
        return ugettext_lazy('Students must pass a set of assignments selected by you')

    def get_description(self):
        return ugettext_lazy('Choose this option if you require your students to get a '
                             'passing grade on a subset of their assignments to qualify for final exams. '
                             'You select the assignments on the next page.')

    def get_viewclass(self):
        return subset_approved.SubsetApprovedView


class ApprovedAppConfig(AppConfig):
    name = 'devilry.devilry_qualifiesforexam_approved'

    def ready(self):
        registry.qualifiesforexam_plugins.add(AllApprovedPluginItem)
        registry.qualifiesforexam_plugins.add(SubsetApprovedPluginItem)
