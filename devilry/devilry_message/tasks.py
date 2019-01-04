import traceback


def prepare_message(message_id, message_class_string, send_when_prepared=False):
    """
    Prepares message for sending.

    Will call the :func:`~.send_message` RQ-task and send the message if
    :obj:`~.ievv.ievv_messageframework.models.BaseMessage.requested_send_datetime` is ``None``.

    This task does the following:
        1. Get the message to send. If this fails it means that the message is still locked on the DB-level, or that
           the status has changed(it's already sent or is queued for sending).

        If 1. is OK, then:

            2. The status is set to ``preparing``.
            3. :obj:`~.ievv.ievv_messageframework.models.MessageReceiver``s are created for the message.
            4. Status is set to ``queued_for_sending``.

        If ``message.requested_send_datetime`` is ``None`` nothing is done and the status
        is still ``queued_for_sending``, else:

            5. send_message RQ task is called, see docs for that function.

    Note::
        Exceptions raised inside the atomic block for starting the sending process is
        added to the message.status_data.

    Args:
        message_id: A ``BaseMessage`` instance id.
    """
    from django.db import transaction
    from django.conf import settings
    from devilry.devilry_message.models import BaseMessage
    from devilry.devilry_message import messageclass_registry
    import logging
    logger = logging.getLogger(__name__)

    message_class = messageclass_registry.Registry\
        .get_instance()\
        .get(message_class_string=message_class_string)

    def get_message(status):
        return message_class.objects \
            .select_for_update(skip_locked=True) \
            .filter(status=status) \
            .get(id=message_id)

    with transaction.atomic():
        try:
            message = get_message(status=BaseMessage.STATUS_CHOICES.QUEUED_FOR_PREPARE.value)
        except message_class.DoesNotExist:
            logger.warning('Another task has already started processing the message with ID #{message_id}.')
            return

        try:
            with transaction.atomic():

                # Set status preparing
                message.status = BaseMessage.STATUS_CHOICES.PREPARING.value
                message.save()

                # Create message receivers
                message.create_message_receivers()

                # Set status queued_for_sending
                if send_when_prepared:
                    message.status = BaseMessage.STATUS_CHOICES.QUEUED_FOR_SENDING.value
                    message.save()

                else:
                    message.status = BaseMessage.STATUS_CHOICES.READY_FOR_SENDING.value
                    message.save()

        except Exception as exception:
            message.status = BaseMessage.STATUS_CHOICES.ERROR.value
            message.status_data = {
                'error_message': str(exception),
                'exception_traceback': traceback.format_exc()
            }
            message.save()
            return

    # Send message
    # if send_when_prepared and message.status == BaseMessage.STATUS_CHOICES.QUEUED_FOR_SENDING.value \
    #         and message.requested_send_datetime is None:
    #     if getattr(settings, 'IEVV_MESSAGEFRAMEWORK_QUEUE_IN_REALTIME', True):
    #         send_message(message_id=message_id, message_class_string=message_class_string)


# def send_message(message_id, message_class_string):
#     """
#     Sends a message with the appropriate backend.
#
#     This task does the following:
#         1. Fetches the message.
#         2. Status is set to ``sending_in_progress``
#         3. Call backends for each message_type in ``message.message_types``, and sent to `MessageReceiver`s.
#            MessageReceiver
#     """
#     from ievv.ievv_messageframework import backend_registry
#     from django.db import transaction
#     from ievv.ievv_messageframework.models import BaseMessage
#     from ievv.ievv_messageframework import messageclass_registry
#     import logging
#     logger = logging.getLogger(__name__)
#
#     message_class = messageclass_registry.Registry\
#         .get_instance()\
#         .get(message_class_string=message_class_string)
#
#     def get_message():
#         return message_class.objects\
#             .select_for_update(skip_locked=True)\
#             .filter(status__in=[BaseMessage.STATUS_CHOICES.QUEUED_FOR_SENDING.value,
#                                 BaseMessage.STATUS_CHOICES.READY_FOR_SENDING.value])\
#             .get(id=message_id)
#
#     with transaction.atomic():
#         try:
#             message = get_message()
#         except message_class.DoesNotExist:
#             logger.warning('Another task has already started processing/sending the message with ID '
#                            '#{message_id}.'.format(message_id=message_id))
#             return
#
#         # Set status sending_in_progress
#         message.status = BaseMessage.STATUS_CHOICES.SENDING_IN_PROGRESS.value
#         message.save()
#
#         for message_type in message.message_types:
#             backend_class = backend_registry.Registry\
#                 .get_instance()\
#                 .get(message_type=message_type)
#             backend = backend_class(
#                 message=message,
#                 message_receivers=message.messagereceiver_set.filter(message_type=message_type))
#             backend.send_messages()
#
#         # Set status sent
#         message.status = BaseMessage.STATUS_CHOICES.SENT.value
#         message.save()
