from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CharField
from django.db.models.functions import Concat

from devilry.devilry_account.models import UserEmail, UserName


def anonymize_user(fast=True):
    """
    Anonymize user and related UserEmail and UserName.

    ``fast=True`` replaces:
     - User.shortname with User.id
     - UserEmail.email with <UserEmail.user_id@example.com>.
     - UserName.username with UserName.user_id.
    """
    if fast:
        # Update user models
        get_user_model().objects.update(
            shortname=Concat(models.F('id'), models.Value(''), output_field=CharField()))
        UserEmail.objects.update(
            email=Concat(models.F('user_id'), models.Value('@example.com'), output_field=CharField()))
        UserName.objects.update(
            username=Concat(models.F('user_id'), models.Value(''), output_field=CharField()))