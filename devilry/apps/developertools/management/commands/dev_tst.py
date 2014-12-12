from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        from devilry.apps.core.models import Deadline
        from devilry.apps.core.models import Assignment
        assignment = Assignment.objects.get(id=1)
        Deadline.objects.smart_create(
            assignment.assignmentgroups.all(), #.filter(id=55),
            deadline_datetime=datetime.now(),
            text='Hello world')