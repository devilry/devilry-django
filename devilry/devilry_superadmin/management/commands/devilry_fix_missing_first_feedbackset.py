from django.core.management.base import BaseCommand
from django.db import connection

from devilry.apps.core.models import AssignmentGroup


class Command(BaseCommand):
    help = 'Fix all missing first feedbacksets. Can happen if ievv customsql -i -r has not been run.'

    def handle(self, *args, **options):
        query = 'select devilry__create_first_feedbackset_in_group(%s, %s)'
        fixed_count = 0
        with connection.cursor() as cursor:
            for group in AssignmentGroup.objects.all():
                if group.feedbackset_set.count() == 0:
                    cursor.execute(query, [group.id, group.parentnode_id])
                    fixed_count += 1
        self.stdout.write('Created first FeedbackSet for {} groups'.format(fixed_count))
