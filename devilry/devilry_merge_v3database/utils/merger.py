# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.contrib.auth import get_user_model
from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models


class AbstractMerger:
    """
    Base merger class containing helper-functions for fetching objects.

    Must be subclassed by model-specific merger classes.
    """

    #: The main model to migrate.
    model = None

    def __init__(self, from_db_alias, to_db_alias='default', transaction=False):
        """

        Args:
            from_db_alias: The database to migrate from.
            to_db_alias: The database to migrate to.
            transaction: Should the migration be run as a single transaction? Defaults to ``False``.
        """
        self.from_db_alias = from_db_alias
        self.to_db_alias = to_db_alias
        self.run_as_single_transaction = transaction

    def get_user_by_shortname(self, shortname):
        """
        Get :obj:`devilry.devilry_account.models.User` by ``shortname`` from current default database.

        Args:
            shortname: The shortname of an user from the database to merge.

        Returns:
            :obj:`devilry.devilry_account.models.User`: User instance from the default database or ``None``.
        """
        try:
            return get_user_model().objects.get(shortname=shortname)
        except get_user_model().DoesNotExist:
            return None

    def get_permissiongroup_by_name(self, name):
        """
        Get :obj:`devilry.devilry_account.models.PermissionGroup` by ``name`` from current database.

        Args:
            name: The unique name of a permission group from the database to merge.

        Returns:
            :obj:`devilry.devilry_account.models.PermissionGroup`: ``PermissionGroup`` instance from the
                default database or ``None``.
        """
        try:
            return account_models.PermissionGroup.objects.get(name=name)
        except account_models.PermissionGroup.DoesNotExist:
            return None

    def get_subject_by_shortname(self, shortname):
        """
        Get :obj:`devilry.apps.core.models.Subject` by ``shortname`` from current default database.

        Returns:
            :obj:`devilry.apps.core.models.Subject`: Subject instance or ``None``.
        """
        try:
            return core_models.Subject.objects.get(short_name=shortname)
        except core_models.Subject.DoesNotExist:
            return None

    def get_period_by_shortname(self, parentnode_shortname, shortname):
        """
        Get :obj:`devilry.apps.core.models.Period` by ``shortname`` from current default database.

        Returns:
            :obj:`devilry.apps.core.models.Period`: Period instance or ``None``.
        """
        try:
            return core_models.Period.objects.get(parentnode__short_name=parentnode_shortname, short_name=shortname)
        except core_models.Period.DoesNotExist:
            return None

    def update_after_save(self, from_db_object):
        """
        Method for updating fields after the object from the migrate database is saved to the `to_db_alias` database.

        Mainly used for updating auto_now and auto_now_add fields as these can only be edited with an QuerySet.update()
        query.

        Args:
            from_db_object: The object from the migrate database.
        """
        pass

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

    def select_related_foreign_keys(self):
        """
        Override this method to return a list of fields that should be used
        in select_related on the QuerySet for the ``self.model``-class.

        Note:
            We need to do a select_related on the queryset the objects are fetched from to get the correct foreign key
            descriptors.

            Here's are a couple of example models (example from Devilry):
                class User(..):
                    ...
                    shortname = models.CharField()

                class UserEmail(..):
                    user = models.ForeignKey(User)
                    ...

            And we have two databases, one database to migrate data into from another database:
                default
                migrate_from

            Example where each database(default and migrate_from) has a user each with different IDs:

                In the example below, the users from each database have different IDs:
                    user in default database has ID 1
                    user in migrate_from database has ID 230

                    for user_email in UserEmail.objects.using("migrate_from").all():
                        # Will raise a UserDoesNotExist-error
                        print user_email.user

                In the example below, both users has the same ID, but different shortnames:
                    # Create a user in the default database.
                    default_db_user = User(id=230, shortname='default_db_user')
                    default_db_user.save()

                    # Create a User and a UserEmail in the migrate_from database.
                    migrate_from_db_user = User(id=230, shortname='migrate_from_db_user')
                    migrate_from_db_user.save(using='migrate_from')
                    UserEmail(user=migrate_from_db_user).save(using='migrate_from')

                    for user_email in UserEmail.objects.using("migrate_from").all():
                        # We expect the result to be 'migrate_from_db_user'.
                        # But since we did not use select_related, the result will be `default_db_user`
                        print user_email.user.shortname

        The reason for this weird behaviour is that Django does a separate query for the user, disregarding
        the `using(..)` filter on the QuerySet and simply uses the default database.

        Adding select_related will fix this, as select_related operates on the database defined by `using(..)`,
        and fetched the users from that database.

        Returns:
            list: A list of foreign key descriptors.
        """
        return []

    def __run(self):
        if self.model is None:
            raise ValueError('{}.model is \'None\''.format(self.__class__.__name__))
        for from_db_object in self.model.objects.using(self.from_db_alias)\
                .select_related(*self.select_related_foreign_keys()).all():
            self.start_migration(from_db_object=from_db_object)
            self.update_after_save(from_db_object=from_db_object)

    def run(self):
        """
        Do not override this! Override :meth:`~.start_migration` instead.

        Initializes the merger with atomic transaction.
        """
        if self.run_as_single_transaction:
            with transaction.atomic():
                self.__run()
        else:
            self.__run()
