# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.contrib.auth import get_user_model
from devilry.apps.core import models as core_models


class AbstractMerger:
    """
    Base merger class containing helper-functions for fetching objects.

    Must be subclassed by model-specific merger classes.
    """

    #: The main model to migrate.
    model = None
    foreign_key_field_to_be_set_manually = ['id']

    def __init__(self, from_db_alias, to_db_alias='default'):
        self.from_db_alias = from_db_alias
        self.to_db_alias = to_db_alias

    def get_user_by_shortname(self, user_id):
        """
        Get :obj:`devilry.devilry_account.models.User` by ``shortname`` from current default database.

        Args:
            user_id: The user id from the merge db object.

        Returns:
            :obj:`devilry.devilry_account.models.User`: User instance.
        """
        mergedb_user = get_user_model().objects.using(self.from_db_alias).get(id=user_id)
        try:
            return get_user_model().objects.get(shortname=mergedb_user.shortname)
        except get_user_model().DoesNotExist:
            return None

    def get_subject_by_shortname(self, shortname):
        """
        Get :obj:`devilry.apps.core.models.Subject` by ``shortname`` from current default database.

        Returns:
            :obj:`devilry.apps.core.models.Subject`: Subject instance.
        """
        try:
            return core_models.Subject.objects.get(short_name=shortname)
        except core_models.Subject.DoesNotExist:
            return None

    def get_period_by_shortname(self, parentnode_shortname, shortname):
        """
        Get :obj:`devilry.apps.core.models.Period` by ``shortname`` from current default database.

        Returns:
            :obj:`devilry.apps.core.models.Period`: Period instance.
        """
        try:
            return core_models.Period.objects.get(parentnode__short_name=parentnode_shortname, short_name=shortname)
        except core_models.Period.DoesNotExist:
            return None

    def save_object(self, obj):
        """
        Ensures the `full_clean()` and that object is saved to the `to_db_alias` database.

        Arg:
            obj: Instance of `self.model`.
        """
        obj.full_clean()
        obj.save(using=self.to_db_alias)


    def start_migration(self, from_db_object):
        """
        Write code for migrating models here.
        """
        raise NotImplementedError()

    def run(self):
        """
        Do not override this! Override :meth:`~.start_migration` instead.

        Initializes the merger with atomic transaction.
        """
        if self.model is None:
            raise ValueError('{}.model is \'None\''.format(self.__class__.__name__))
        for from_db_object in self.model.objects.using(self.from_db_alias).all():
            self.start_migration(from_db_object=from_db_object)
