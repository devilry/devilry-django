# -*- coding: utf-8 -*-


from django.core.management.base import BaseCommand
from devilry.devilry_message.models import Message


class Command(BaseCommand):
    """
    Management command for deleting messages without any message receivers.
    """
    help = 'Delete messages without any message receivers'

    def handle(self, *args, **options):
        messages = Message.objects.filter_message_with_no_message_receivers()
        self.stdout.write('Deleting {} messages with no message receivers.'.format(messages.count()))
        messages.delete()
