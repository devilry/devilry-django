# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import Lower, Concat

from devilry.apps.core.models import Examiner, Candidate, AssignmentGroup
from devilry.devilry_dbcache.models import AssignmentGroupCachedData


class DevilryGroupCrInstanceMixin(object):
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'feedbackfeed'

    def _get_base_rolequeryset(self):
        """Get base rolequerysets used by subclasses.

        Get :class:`~devilry.apps.core.models.AssignmentGroup`s and prefetch related
        :class:`~devilry.apps.core.models.Examiner`s and :class:`~devilry.apps.core.models.Candidate`s.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s.

        """
        return AssignmentGroup.objects \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count() \
            .select_related('parentnode__parentnode__parentnode') \
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self._get_candidatequeryset())) \
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self._get_examinerqueryset())) \
            .prefetch_related(
                models.Prefetch('cached_data',
                                queryset=self._get_assignment_group_cacheddata_queryset()))

    def _get_candidatequeryset(self):
        """Get candidates.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Candidate`s.
        """
        return Candidate.objects \
            .select_related('relatedstudent') \
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))

    def _get_examinerqueryset(self):
        """Get examiners.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Examiner`s.
        """
        return Examiner.objects \
            .select_related('relatedexaminer') \
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

    def _get_assignment_group_cacheddata_queryset(self):
        return AssignmentGroupCachedData.objects\
            .select_related(
                'group',
                'first_feedbackset',
                'last_feedbackset',
                'last_published_feedbackset')

    def get_titletext_for_role(self, role):
        """String representation for the role.

        Args:
            role: An :obj:`~devilry.apps.core.models.AssignmentGroup`
                instance of the roleclass for the crinstance.

        Returns:
            str: Formatted string reprensentation of the crinstance role.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)
