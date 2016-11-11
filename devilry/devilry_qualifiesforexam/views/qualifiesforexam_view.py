
# CrAdmin imports
from django.views.generic import TemplateView
from django_cradmin.viewhelpers import objecttable

# Devilry imports
from devilry.apps.core import models as core_models
from devilry.utils import groups_groupedby_relatedstudent_and_assignment


class QualificationBaseView(TemplateView):

    model = core_models.Assignment
    template_name = ''

    # def get_queryset_for_role(self, role):
    #     queryset = self.model.objects.filter(parentnode__id=role.id)
    #     return queryset
