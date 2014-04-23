from django.views.generic import TemplateView
from django.http import Http404

from devilry.apps.core.models import AssignmentGroup


class GroupDetailsView(TemplateView):
    template_name = 'devilry_student/groupdetails.django.html'

    def _get_group(self):
        try:
            return AssignmentGroup.objects\
                    .filter_student_has_access(self.request.user)\
                    .select_related(
                        'last_deadline',
                        'parentnode', # Assignment
                        'parentnode__parentnode', # Period
                        'parentnode__parentnode__parentnode', # Subject
                    )\
                    .prefetch_related(
                        'candidates',
                        'examiners'
                    )\
                    .get(id=self.kwargs['id'])
        except AssignmentGroup.DoesNotExist:
            raise Http404()


    def get_context_data(self, **kwargs):
        context = super(GroupDetailsView, self).get_context_data(**kwargs)
        group = self._get_group()
        context['group'] = group
        context['deadlines'] = group.deadlines.all()
        return context