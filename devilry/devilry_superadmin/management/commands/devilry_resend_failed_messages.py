# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """
    Management command for periodically resending messages with status `failed` to
    users.
    """
    help = 'Management command that can be used to resend messages with status `failed` and ' \
           'the failed send count is not greater than DEVILRY_MESSAGE_RESEND_LIMIT in settings.'

    def handle(self, *args, **options):
        from devilry.devilry_message.models import MessageReceiver
        from django.conf import settings

        # Get all failed messages
        failed_message_receivers = MessageReceiver.objects\
            .filter(status=MessageReceiver.STATUS_CHOICES.FAILED.value)

        # Get the number of failed messages that exceeded the limit.
        exceeded_resend_limit_count = failed_message_receivers\
            .filter(sending_failed_count__gt=settings.DEVILRY_MESSAGE_RESEND_LIMIT).count()

        # Get all failed messaged that has not yet exceeded the resend limit
        failed_message_receivers = failed_message_receivers \
            .filter(sending_failed_count__lte=settings.DEVILRY_MESSAGE_RESEND_LIMIT)

        # Get the number of failed messaged that has not yet exceeded the resend limit
        failed_message_receivers_count = failed_message_receivers.count()

        with transaction.atomic():
            for message_receiver in failed_message_receivers:
                message_receiver.send()

        self.stdout.write(
            '{num_resent} messages were automatically resent.\n'
            '{exceeded_resend_limit} messages has exceeded the retry limit '
            '(current limit: {resend_limit})'.format(
                num_resent=failed_message_receivers_count,
                exceeded_resend_limit=exceeded_resend_limit_count,
                resend_limit=settings.DEVILRY_MESSAGE_RESEND_LIMIT
            ))
