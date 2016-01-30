from __future__ import unicode_literals

from django.http import Http404

from devilry.apps.core.models import RelatedExaminer


class SingleExaminerViewMixin(object):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/examiners/examinerdetails.django.html'

    def get_relatedexaminer_id(self):
        return self.kwargs['relatedexaminer_id']

    def get_relatedexaminer_queryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .annotate_with_number_of_groups_on_assignment(assignment=assignment)\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=assignment)\
            .exclude(active=False)
        return queryset

    def __get_relatedexaminer(self):
        try:
            return self.get_relatedexaminer_queryset().get(id=self.get_relatedexaminer_id())
        except RelatedExaminer.DoesNotExist:
            raise Http404()

    def get_relatedexaminer(self):
        if not hasattr(self, '_relatedexaminer'):
            self._relatedexaminer = self.__get_relatedexaminer()
        return self._relatedexaminer
