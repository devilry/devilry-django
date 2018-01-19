import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from ievv_opensource.ievv_batchframework.models import BatchOperation

from devilry.apps.core.models import Subject, AssignmentGroup
from devilry.devilry_account.models import UserEmail, UserName


def model_sort_keyfunction(model_class):
    prefix = '99'
    if model_class == BatchOperation:
        prefix = '00'
    if model_class == BatchOperation:
        prefix = '00'
    elif model_class == AssignmentGroup:
        prefix = '01'
    elif model_class == Subject:
        prefix = '02'
    return '{}-{}'.format(prefix, model_class.__name__)


class Command(BaseCommand):
    help = 'Delete all data in the database except for users.'

    def handle(self, *args, **kwargs):
        djangoenv = os.environ.get('DJANGOENV', 'develop')
        if not settings.DEBUG or djangoenv != 'develop':
            self.stderr.write(
                'You can not run this script unless you are in development mode. This means '
                'that DEBUG must be False, and DJANGOENV must be "develop".')
            raise SystemExit()
        user_model = get_user_model()
        skipped_model_classes = {
            user_model, UserEmail, UserName,
            Site
        }
        with transaction.atomic():
            for model_class in sorted(apps.get_models(), key=model_sort_keyfunction):
                if model_class in skipped_model_classes:
                    self.stdout.write('Not deleting {}'.format(model_class.__name__))
                    continue
                self.stdout.write('Deleting all rows in {}'.format(model_class.__name__))
                model_class.objects.all().delete()
