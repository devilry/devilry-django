from __future__ import unicode_literals

from django_cradmin.viewhelpers.update import UpdateView

from devilry.apps.core import models as coremodels


class AssignmentGradingConfigurationUpdateView(UpdateView):
    model = coremodels.Assignment

    fields = ['grading_system_plugin_id',
              'points_to_grade_mapper',
              'max_points',
              'passing_grade_min_points']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.request.cradmin_role.id)
