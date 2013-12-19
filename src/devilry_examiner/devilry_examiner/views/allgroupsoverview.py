from django.views.generic import DetailView

from devilry.apps.core.models import Assignment


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get_queryset(self):
        if self.request.GET.get('waiting_for_feedback'):
            print "hei"
        else:
            print "heia"

        return Assignment.examiner_objects.filter_is_examiner(self.request.user)
