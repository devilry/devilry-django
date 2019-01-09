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

        failed_message_receivers = MessageReceiver.objects\
            .filter(
                status=MessageReceiver.STATUS_CHOICES.FAILED.value,
                sending_failed_count__lte=settings.DEVILRY_MESSAGE_RESEND_LIMIT
            )

        with transaction.atomic():
            for message_recevier in failed_message_receivers:
                message_recevier.send()
