# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.db import models as db_models
from django.db.models.functions import Lower, Concat

# CrAdmin imports
from django.http import Http404
from django_cradmin import crinstance

# Devilry imports
from devilry.devilry_cradmin import devilry_crmenu
from devilry.apps.core import models as core_models
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_qualifiesforexam import cradmin_app


class Menu(devilry_crmenu.Menu):
    devilry_role = 'admin'

    def build_menu(self):
        period = self.request.cradmin_role


class CrInstance(crinstance.BaseCrAdminInstance):
    """
    CrInstance that defines access rights and role management for this app.
    """

    roleclass = core_models.Period
    rolefrontpage_appname = 'qualifiesforexam'
    menuclass = Menu

    apps = [
        ('qualifiesforexam', cradmin_app.App)
    ]

    id = 'devilry_qualifiesforexam'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_qualifiesforexam')

    def is_admin(self):
        """
        Checks if the user has access.

        A user must be an admin for this Period or above to gain access to this app.

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
        Get queryset of :class:`~devilry.apps.core.models.Period` with join on the ``Periods``s
        related :class:`~devilry.apps.core.models.Subject`.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.Period`

        """
        return core_models.Period.objects\
            .select_related('parentnode')\
            .filter_user_is_admin(user=self.request.user)

    def get_titletext_for_role(self, role):
        return str(role)
