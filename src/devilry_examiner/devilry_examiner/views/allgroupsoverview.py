from django.views.generic import DetailView

from devilry.apps.core.models import Assignment


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get_queryset(self):
        return Assignment.examiner_objects.where_is_examiner(self.request.user)
