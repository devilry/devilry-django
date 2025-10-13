from django.conf import settings
from django.core import mail
from django_rq import job


@job(settings.DEVILRY_MESSAGE_RQ_QUEUENAME)
def async_send_message_receiver(message_receiver_id):
    from devilry.devilry_message.models import MessageReceiver
    message_receiver = MessageReceiver.objects.get(id=message_receiver_id)
    message_receiver.sync_send()
