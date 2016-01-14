from django.core.urlresolvers import reverse
from django.views.generic.detail import SingleObjectMixin
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import Assignment
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError


class AssignmentSingleObjectMixin(SingleObjectMixin):
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_user_is_admin(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject


class WizardStep(object):
    def __init__(self, wizard_steps, slug, title, index):
        self.wizard_steps = wizard_steps
        self.slug = slug
        self.title = title
        self.index = index

    def get_number(self):
        return self.index + 1

    def get_total(self):
        return len(self.wizard_steps)

    def get_percent(self):
        return int(float(self.get_number()) / len(self.wizard_steps) * 100)

    def get_url(self):
        urlname = 'devilry_gradingsystem_admin_{}'.format(self.slug)
        return reverse(urlname, kwargs={
            'assignmentid': self.wizard_steps.assignment.id
        })

    def get_previous_url(self):
        if self.index == 0:
            return reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
                'assignmentid': self.wizard_steps.assignment.id
            })
        else:
            return self.wizard_steps.get_by_index(self.index-1).get_url()

    def is_last(self):
        return self.index == len(self.wizard_steps) - 1

class WizardSteps(object):
    def __init__(self, assignment):
        self.assignment = assignment
        pluginapi = assignment.get_gradingsystem_plugin_api()
        self.ordered = []
        self.by_slug = {}

        if pluginapi.requires_configuration:
            self.add_step('configure_plugin', _('Configure'))
        if not pluginapi.sets_max_points_automatically:
            self.add_step('setmaxpoints', _('Set the maximum possible number of points'))
        self.add_step('select_points_to_grade_mapper', _('Select how results are presented to the students'))
        if assignment.points_to_grade_mapper == 'custom-table':
            self.add_step('setup_custom_table', _('Map points to grade'))
        if not pluginapi.sets_passing_grade_min_points_automatically:
            self.add_step('setpassing_grade_min_points', _('Set the minumum number of points required to pass'))

    def add_step(self, slug, title):
        index = len(self.ordered)
        entry = WizardStep(self, slug, title, index)
        self.ordered.append(entry)
        self.by_slug[slug] = entry

    def get_by_slug(self, slug):
        return self.by_slug[slug]

    def get_by_index(self, index):
        return self.ordered[index]

    def __len__(self):
        return len(self.ordered)


class AssignmentSingleObjectRequiresValidPluginMixin(AssignmentSingleObjectMixin):
    def get_object(self):
        assignment = super(AssignmentSingleObjectRequiresValidPluginMixin, self).get_object()
        try:
            assignment.get_gradingsystem_plugin_api()
        except GradingSystemPluginNotInRegistryError:
            raise Http404()
        return assignment

    def get_wizard_step_map(self):
        assignment = self.object
        return WizardSteps(assignment)
