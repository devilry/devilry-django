# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.db.models.functions import Lower, Concat
from django.db import models as db_models

# CrAdmin imports
from django.http import Http404
from django_cradmin import crinstance, crmenu

# Devilry imports
from devilry.apps.core import models as core_models
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_qualifiesforexam.views import selecplugin_view


class Menu(crmenu.Menu):
    devilry_role = 'admin'

    def build_menu(self):
        period = self.request.cradmin_role
        self.add_headeritem(
            label=period.subject.long_name,
            url=self.appindex_url('selectplugin'))


class CrInstance(crinstance.BaseCrAdminInstance):
    """
    CrInstance that defines access rights and role management for this app.
    """
    roleclass = core_models.Period
    rolefrontpage_appname = 'qualifiesforexam'

    menuclass = Menu
    apps = [
        ('selectplugin', selecplugin_view.App)
    ]

    id = 'devilry_qualifiesforexam'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_qualifiesforexam')

    def is_admin(self):
        """
        Checks if the user has access.

        A user must be an admin for this Period to gain access to this app.

        Returns:
            str: The role of the user.

        Raises:
            Http404: If user is not admin for this Period.
        """
        role = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=self.request.cradmin_role
        )
        if role is None:
            raise Http404
        return role

    def get_rolequeryset(self):
        """
        Get queryset of :class:`~devilry.apps.core.models.Period` that belongs to a Period
        with related :class:`~devilry.apps.core.models.Candidate`s.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Period`

        """
        queryset = core_models.Period.objects\
            .select_related('parentnode')\
            .prefetch_related(
                db_models.Prefetch('assignments',
                                   queryset=self.__get_assignment_queryset()))
        return queryset.filter_user_is_admin(user=self.request.user)

    def __get_assignment_queryset(self):
        """
        Prefetch related Assignments.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Assignment`s
        """
        return core_models.Assignment.objects\
            .select_related('parentnode__parentnode')\
            .prefetch_related(
                db_models.Prefetch('assignmentgroups',
                                   queryset=self.__get_assignmentgroup_queryset()))

    def __get_assignmentgroup_queryset(self):
        """
        Prefetch related AssignmentGroups

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s.
        """
        return core_models.AssignmentGroup.objects\
            .select_related('parentnode__parentnode__parentnode')\
            .prefetch_related(
                db_models.Prefetch('candidates',
                                   queryset=self.__get_candidate_queryset()))

    def __get_candidate_queryset(self):
        """
        Prefetch related :class:`~devilry.apps.core.models.Candidate`s for the period.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Candidates`s.
        """
        # return core_models.Candidate.objects\
        #     .select_related('assignment_group__parentnode__parentnode')\
        #     .prefetch_related(db_models.Prefetch('relatedstudent'))
        return core_models.Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
