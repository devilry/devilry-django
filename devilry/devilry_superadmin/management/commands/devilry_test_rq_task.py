from django.core.management.base import BaseCommand, CommandError

import django_rq

from devilry.utils.management import add_input_encoding_argument
from devilry.devilry_superadmin import tasks


class Command(BaseCommand):
    help = 'Create new user.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            default='default',
            help='RQ queue. Which queue the task should run on.'),
        add_input_encoding_argument(parser)

    def handle(self, *args, **options):
        queue = options['queue']
        queue = django_rq.get_queue(name=queue)
        queue.enqueue(tasks.add, 3, 5)

