# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.devilry_account import models as account_models
from django.conf import settings
from django.contrib.auth import get_user_model


class UserMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.User` from database to
    current default database.
    """
    model = get_user_model()

    def start_migration(self, from_db_object):
        user = self.get_user_by_shortname(shortname=from_db_object.shortname)
        if not user:
            new_user_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk'])
            new_user = get_user_model()(**new_user_kwargs)
            self.save_object(obj=new_user)


class UserNameMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.UserName` from database to
    current default database.
    """
    model = account_models.UserName

    def selectd_related_foreign_keys(self):
        return ['user']

    def start_migration(self, from_db_object):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            return

        existing_usernames = account_models.UserName.objects \
            .values_list('username', flat=True)
        if from_db_object.username not in existing_usernames:
            user = self.get_user_by_shortname(shortname=from_db_object.user.shortname)
            username_kwargs = model_to_dict(from_db_object, exclude=['id', 'user', 'pk'])
            username = account_models.UserName(**username_kwargs)
            username.user_id = user.id
            username.created_datetime = from_db_object.created_datetime
            username.last_updated_datetime = from_db_object.last_updated_datetime
            self.save_object(obj=username)


class UserEmailMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_account.models.UserEmail` from database to
    current default database.
    """
    model = account_models.UserEmail

    def selectd_related_foreign_keys(self):
        return ['user']

    def start_migration(self, from_db_object):
        existing_useremails = account_models.UserEmail.objects\
            .values_list('email', flat=True)
        if from_db_object.email not in existing_useremails:
            user = self.get_user_by_shortname(shortname=from_db_object.user.shortname)
            user_email_kwargs = model_to_dict(from_db_object, exclude=['id', 'user', 'pk'])
            user_email = account_models.UserEmail(**user_email_kwargs)
            user_email.user_id = user.id
            user_email.created_datetime = from_db_object.created_datetime
            user_email.last_updated_datetime = from_db_object.last_updated_datetime
            self.save_object(obj=user_email)

