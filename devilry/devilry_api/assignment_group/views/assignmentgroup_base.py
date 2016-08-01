from django.db import models
from django.db.models.functions import Lower, Concat
from rest_framework.generics import ListAPIView

from devilry.apps.core.models.candidate import Candidate
from devilry.apps.core.models.examiner import Examiner
from devilry.devilry_api.auth.authentication import TokenAuthentication


class AssignmentGroupListViewBase(ListAPIView):
    authentication_classes = (TokenAuthentication, )

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_query_set(self):
        raise NotImplementedError()

    def get_queryset(self):
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent__user') \
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        examinerqueryset = Examiner.objects \
            .select_related('relatedexaminer__user') \
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

        queryset = self.get_role_query_set() \
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset)) \
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=examinerqueryset)) \
            .annotate_with_grading_points() \
            .annotate_with_is_waiting_for_feedback() \
            .annotate_with_is_waiting_for_deliveries() \
            .annotate_with_is_corrected() \
            .distinct()
        return queryset

    def get(self, request, *args, **kwargs):
        return super(AssignmentGroupListViewBase, self).get(request, *args, **kwargs)
