#!/usr/bin/env python
import django
import os

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction


class ProgressPrintIterator:
    """
    Progress print iterator. Useful to print progress of long running scripts.

    (Copied from ievv_opensource since we are a bit behind on the versions in master)

    Example::

        queryset = MyModel.objects
        total = queryset.count()
        for obj, is_end_of_group in ProgressPrintIterator(
                iterator=queryset.iterator(),
                total_count=total,
                what='Doing something',
                items_per_group=500):
            # Do something with ``obj``. If you want to do something after 500 items has been processed
            # including the last iteration (which may be less than 500 items),
            # use ``if is_end_of_group``
    """
    def __init__(self, iterator, total_count, what, items_per_group=500, log_function=None):
        """

        Args:
            iterator: Some iterator, such as a ``queryset.iterator()``.
            total_count: Total number of items.
            what: A message to print when printing progress
            items_per_group: Items per group - we print progress each time we have processed this number of items.
            log_function: A log function. For management scripts, you want to set this to ``self.stdout.write``.
        """
        self.iterator = iterator
        self.total_count = total_count
        self.what = what
        self.items_per_group = items_per_group
        self.log_function = log_function or print

    def __iter__(self):
        start_time = timezone.now()
        for index, item in enumerate(self.iterator, start=1):
            progress_percent = index / self.total_count * 100
            is_end_of_group = (index % self.items_per_group == 0) or (index == self.total_count)
            yield item, is_end_of_group
            if is_end_of_group:
                now = timezone.now()
                time_used = now - start_time
                if progress_percent > 0:
                    estimated_end_delta = time_used / progress_percent * (100 - progress_percent)
                    estimated_end_minutes = round(estimated_end_delta.total_seconds() / 60, 2)
                else:
                    estimated_end_minutes = 'UNKNOWN'
                self.log_function(
                    f'{round(progress_percent, 1)}% [{index}/{self.total_count}]: {self.what}. '
                    f'Est. minutes remaining: {estimated_end_minutes}')


def update_notifications_for_user(user):
    """
    Swap from one email suffix to another, and set the primary and notification
    email to the email address maching the new suffix.
    """
    from devilry.devilry_account.models import UserEmail
    from_email_suffixes = ['@old.shit.example.com', '@oldstuff.example.com', '@superoldstuff.example.com']
    new_primary_email_suffix = '@example.com'

    # Convert from old to new primary
    for from_email_suffix in from_email_suffixes:
        if user.useremail_set.filter(email__endswith=from_email_suffix).exists():
            matched_email = user.useremail_set.filter(email__endswith=from_email_suffix).first()
            username = matched_email.email.split('@')[0]
            new_email = f'{username}{new_primary_email_suffix}'

            # Prevent generating duplicates (which is an IntegrityError enforced by the unique constraint in the database)
            if not UserEmail.objects.filter(email=new_email).exists():
                matched_email.email = new_email
                matched_email.save()

    # Force notifications and "is_primary" to the `new_primary_email_suffix`
    new_primary_email = user.useremail_set.filter(email__endswith=new_primary_email_suffix).first()
    if new_primary_email is not None:
        user.useremail_set.update(use_for_notifications=False, is_primary=None)
        new_primary_email.use_for_notifications = True
        new_primary_email.is_primary = True
        new_primary_email.clean()
        new_primary_email.save()


if __name__ == "__main__":
    # For development:
    os.environ.setdefault('DJANGOENV', 'develop')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devilry.project.settingsproxy")
    django.setup()

    # For production: Specify python path to your settings file here
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devilry_settings')
    # django.setup()

    user_queryset = get_user_model().objects
    for user, is_end_of_group in ProgressPrintIterator(
            iterator=user_queryset.iterator(),
            total_count=user_queryset.count(),
            what='Processing users',
            items_per_group=300):
        with transaction.atomic():
            update_notifications_for_user(user=user)
