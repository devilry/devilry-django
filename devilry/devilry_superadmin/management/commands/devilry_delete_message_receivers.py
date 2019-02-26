# -*- coding: utf-8 -*-


import arrow
from django.core.management.base import BaseCommand
from devilry.devilry_message.models import MessageReceiver


class Command(BaseCommand):
    """
    Management script for deleting message receivers older than specified number of days ago.
    """
    args = '<num_days>'
    help = 'Delete message receivers older than x number of days.'

    def add_arguments(self, parser):
        parser.add_argument(
            'num_days',
            type=int,
            help='Delete all message receivers older than given number of days ago.'
        )

    def get_datetime_from_days_ago(self, days_ago):
        return arrow.now().replace(days=-days_ago).datetime

    def handle(self, *args, **options):
        num_days = options['num_days']
        delete_older_than_datetime = self.get_datetime_from_days_ago(days_ago=num_days).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Delete MessageReceivers
        message_receivers = MessageReceiver.objects.filter_old_receivers(datetime_obj=delete_older_than_datetime)
        self.stdout.write('Deleting {} message receivers.'.format(message_receivers.count()))
        message_receivers.delete()
