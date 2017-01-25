# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.db import models
from django.db.models.functions import Lower, Concat

# Devilry/cradmin imports
from django_cradmin import crinstance
from devilry.apps.core.models import Examiner, Candidate, AssignmentGroup


class CrInstanceBase(crinstance.BaseCrAdminInstance):
    """Base CrInstance class for crinstances in devilry_group.
    """
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'feedbackfeed'

    def _get_base_rolequeryset(self):
        """Get base rolequerysets used by subclasses.

        Get :class:`~devilry.apps.core.models.AssignmentGroup`s and prefetch related
        :class:`~devilry.apps.core.models.Examiner`s and :class:`~devilry.apps.core.models.Candidate`s.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s.

        """
        return AssignmentGroup.objects\
            .select_related('parentnode__parentnode__parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self._get_candidatequeryset()))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self._get_examinerqueryset()))

    def _get_candidatequeryset(self):
        """Get candidates.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Candidate`s.
        """
        return Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))

    def _get_examinerqueryset(self):
        """Get examiners.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Examiner`s.
        """
        return Examiner.objects\
            .select_related('relatedexaminer')\
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

    def get_titletext_for_role(self, role):
        """String representation for the role.

        Args:
            role: An :obj:`~devilry.apps.core.models.AssignmentGroup`
                instance of the roleclass for the crinstance.

        Returns:
            str: Formatted string reprensentation of the crinstance role.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)

    def get_devilryrole_for_requestuser(self):
        """Get devilry role for the user.

        Get the devilryrole for the requesting user on the current
        assignmentrole (request.cradmin_instance).

        Return:
            str: The return values is the same as for
                :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
                except that this method raises ValueError if it does not find a role or NotImplementedError if this
                class is not subclassed.

        Raises:
            NotImplementedError: Raised if implemented by subclass.
        """
        raise NotImplementedError('Must be implemented by subclass.')

    def add_extra_instance_variables_to_request(self, request):
        setattr(request, 'devilryrole', self.get_devilryrole_for_requestuser())
