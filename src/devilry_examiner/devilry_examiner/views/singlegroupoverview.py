from django.views.generic import DetailView
#from django.http import Http404

from devilry.apps.core.models import AssignmentGroup


class SingleGroupOverview(DetailView):
    template_name = "devilry_examiner/singlegroupoverview.django.html"
    model = AssignmentGroup
    pk_url_kwarg = 'groupid'
    context_object_name = 'group'

    def get_queryset(self):
        return AssignmentGroup.examiner_objects.filter_is_examiner(self.request.user).filter_is_active()

    # def get_context_data(self, **kwargs):
    #     context = super(SingleGroupOverview, self).get_context_data(**kwargs)
    #     return context