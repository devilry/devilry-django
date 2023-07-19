# -*- coding: utf-8 -*-


import traceback

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.contrib.postgres.fields import ArrayField
from django.utils import translation

from cradmin_legacy.apps.cradmin_email import emailutils

from ievv_opensource.utils import choices_with_meta

from devilry.devilry_email.utils import activate_translation_for_user
from devilry.utils.devilry_email import send_message


class MessageQuerySet(models.QuerySet):
    def filter_message_with_no_message_receivers(self):
        """
        Filter all :obj:`.Message`s without any :class:`.MessageReceiver`s.
        """
        return self.annotate(receiver_count=models.Count('messagereceiver'))\
            .filter(receiver_count=0)


class Message(models.Model):
    """
    The `Message`-class handles preparing and sending of different messages in the Devilry-system.

    This model contains metadata about a message sent to one or multiple users, what type of message it is, the overall
    status of the message and creates recipients for the email to be sent.

    Notes:
        The actual subject and message-content is stored on each :class:`.MessageReceiver` with a
        foreignkey to this class. The reason for this being that we want to save the subject and content
        in the preferred language of the user.
    """
    objects = MessageQuerySet.as_manager()

    #: When the message was created.
    created_datetime = models.DateTimeField(
        blank=True, null=True, default=timezone.now
    )

    #: The user that created the message.
    #:
    #: This field may be ``None`` as we need to support system message and
    #: other messages with no specific user.
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL
    )

    #: Choices for :obj:`~.BaseMessage.status`.
    #:
    #: - ``draft``: The message is in the draft state. This means that
    #:   it has not been queued for sending yet, and can still be changed.
    #: - ``preparing``: The message is being prepared for sending. This
    #:   means that a background task is creating :class:`.MessageReceiver`
    #:   objects for the message.
    #: - ``sending``: A background task is sending the message.
    #: - ``error``: Something went wrong. Details in :obj:`~.BaseMessage.status_data`.
    #: - ``sent``: The message has been sent without any errors.
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='draft',
                                 label=gettext_lazy('Draft')),
        choices_with_meta.Choice(value='preparing',
                                 label=gettext_lazy('Preparing for sending'),
                                 description=gettext_lazy('Building the list of actual users to send to.')),
        choices_with_meta.Choice(value='sending',
                                 label=gettext_lazy('Sending')),
        choices_with_meta.Choice(value='error',
                                 label=gettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=gettext_lazy('Sent'))
    )

    #: The "send"-status of a message.
    #:
    #: See :attr:`.BaseMessage.STATUS_CHOICES`.
    status = models.CharField(
        max_length=30,
        db_index=True,
        choices=STATUS_CHOICES.iter_as_django_choices_short(),
        default=STATUS_CHOICES.DRAFT.value
    )

    #: Extra data for the :obj:`~.Message.status` as JSON.
    status_data = models.JSONField(null=False, blank=True, default=dict)

    #: Extra metadata for the message receiver as JSON. This can be anything.
    metadata = models.JSONField(null=False, blank=True, default=dict)

    #: The available context types of the message.
    #:
    #: The purpose of the context type is to provide better
    #: filtering options.
    #:
    #: - `other`: Unspecified type.
    #: - `comment`: Message regarding new comment/delivery.
    #: - `deadline_moved`: Message regarding a moved deadline.
    #: - `feedback`: Message regarding feedback/grading.
    #: - `feedback_updated`: Message regarding an updated grade/result.
    CONTEXT_TYPE_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='other',
                                 label='Other'),
        choices_with_meta.Choice(value='comment_delivery',
                                 label='Comment or delivery'),
        choices_with_meta.Choice(value='deadline_moved',
                                 label='Deadline moved'),
        choices_with_meta.Choice(value='new_attempt',
                                 label='New attempt'),
        choices_with_meta.Choice(value='feedback',
                                 label='Feedback'),
        choices_with_meta.Choice(value='feedback_updated',
                                 label='Grading updated'),
        choices_with_meta.Choice(value='group_invite_invitation',
                                 label='Group invitation: invitation'),
        choices_with_meta.Choice(value='group_invite_accepted',
                                 label='Group invitation: accepted'),
        choices_with_meta.Choice(value='group_invite_rejected',
                                 label='Group invitation: rejected'),
    )

    #: The context type of the message.
    #: See `CONTEXT_TYPE_CHOICES` for more info.
    context_type = models.CharField(
        max_length=255,
        blank=False, null=False,
        choices=CONTEXT_TYPE_CHOICES.iter_as_django_choices_short(),
        default=CONTEXT_TYPE_CHOICES.OTHER.value
    )

    #: ArrayField with the types for this message.
    #:
    #: Examples:
    #: - ``['email']``: Send as email only.
    message_type = ArrayField(
        models.CharField(max_length=30),
        blank=False, null=False
    )

    #: Store data needed to create :class:`.MessageReceiver`-objects.
    #:
    #: Each subclass defines how the dataformat of this field should be.
    #: Override :obj:`.Message.prepare_message_receivers` to create message receivers
    #: from this field.
    virtual_message_receivers = models.JSONField(
        null=False, blank=True, default=dict)

    def prepare_message_receivers(self, subject_generator, template_name, template_context):
        """
        Prepare :class:`.MessageReceiver` objects for :meth:`.create_message_receivers`.
        By _prepare_, we mean to make the MessageReceiver objects, but not save
        them to the database.

        Saving is handled with a bulk create in :meth:`.create_message_receivers`.

        Must return a list of :class:`.MessageReceiver` objects, or a
        generator that yields lists of :class:`.MessageReceiver` objects.
        """
        user_queryset = get_user_model().objects.filter(id__in=self.virtual_message_receivers['user_ids'])
        message_receivers = []
        for user in user_queryset.iterator():
            message_receiver = MessageReceiver.objects.create_receiver(
                user=user,
                message=self,
                message_type=self.message_type[0],
                subject_generator=subject_generator,
                template_name=template_name,
                template_context=template_context
            )
            message_receivers.append(
                message_receiver
            )
        return message_receivers

    def validate_virtual_message_receivers(self):
        """
        This method can be overriden to add custom validation for
        :attr:`.BaseMessage.virtual_message_receivers` in subclasses.

        Does nothing by default.
        """
        if 'user_ids' not in self.virtual_message_receivers:
            raise ValueError('Missing \'user_ids\' in \'virtual_message_receivers\'')
        if type(self.virtual_message_receivers['user_ids']) != list:
            raise ValueError('\'user_ids\' in \'virtual_message_receivers\' is not a list')
        if len(self.virtual_message_receivers['user_ids']) == 0:
            raise ValueError('\'user_ids\' in \'virtual_message_receivers\' is empty')
        for user_id in self.virtual_message_receivers['user_ids']:
            if not isinstance(user_id, int):
                raise ValueError(
                    '\'virtual_message_receivers["user_ids"]\' contains a non-integer value.: {}'.format(user_id))

    def create_message_receivers(self, **kwargs):
        """
        Creates message receivers from list returned from
        :meth:`.BaseMessage.prepare_message_receivers`
        """
        message_receivers = self.prepare_message_receivers(**kwargs)
        MessageReceiver.objects.bulk_create(message_receivers)

    def prepare_and_send(self, subject_generator, template_name, template_context):
        """
        Prepare and send message to message receivers.

        1. Create :class:`.MessageReceiver`s for this message. Set status to `preparing`.
        2. Send message to :class:`.MessageReceover`s for this message. Set status to `sending`.
        3. Set status to `sent`.

        Raises:
            `ValueError` if the status of a the message is not `draft`. A message that
            is not a draft can not be resent via this method.
        """
        self.validate_virtual_message_receivers()
        if not self.status == self.STATUS_CHOICES.DRAFT.value:
            raise ValueError('Can only send drafted messages.')
        with transaction.atomic():
            try:
                # Prepare message receivers. Set status to 'preparing'.
                self.status = self.STATUS_CHOICES.PREPARING.value
                self.save()
                self.create_message_receivers(
                    subject_generator=subject_generator,
                    template_name=template_name,
                    template_context=template_context
                )

                # Send to receivers. Set status to 'sending'.
                self.status = self.STATUS_CHOICES.SENDING.value
                self.save()

                for message_receiver in self.messagereceiver_set.select_related('user').all():
                    message_receiver.send()

                # Set status to 'sent'.
                self.status = self.STATUS_CHOICES.SENT.value
                self.save()
            except Exception as exception:
                self.status = self.STATUS_CHOICES.ERROR.value

                if 'errors' in self.status_data:
                    self.status_data['errors'].append({
                        'error_message': str(exception),
                        'timestamp': timezone.now().isoformat(),
                        'exception_traceback': traceback.format_exc()
                    })
                else:
                    self.status_data = {
                        'errors': [{
                            'error_message': str(exception),
                            'timestamp': timezone.now().isoformat(),
                            'exception_traceback': traceback.format_exc()
                        }]
                    }
                self.save()

    def clean_message_type(self):
        """
        Sets `email` as default message type if empty or `None`.
        """
        if not self.message_type:
            self.message_type = ['email']

    def clean(self):
        self.clean_message_type()

    def __str__(self):
        return 'Message - {} - {}'.format(self.context_type, self.created_datetime)


class MessageReceiverQuerySet(models.QuerySet):
    def create_receiver(self, user, message, message_type, subject_generator, template_name, template_context):
        """
        Create a message receiver and generate the email content and subject
        according to the preferred language of the user and return the `MessageReceiver`-instance. This method
        cleans the receiver object, but DOES NOT SAVE IT.

        Args:
            user: A :class:`devilry.devilry_account.models.User`-instance.
            message: A :class:`.Message`-instance this receiver belongs to.
            message_type: The type of message (email, sms, ...).
            subject_generator: A subclass of
                :class:`devilry.devilry_message.utils.subject_generator.SubjectTextGenerator`
            template_name: Template to render content with (a path).
            template_context: Context data for template.

        Returns:
            :class:`.MessageRecveiver`: Unsaved instance.
        """
        current_language = translation.get_language()
        activate_translation_for_user(user=user)
        message_receiver = MessageReceiver(
            user=user,
            message=message,
            message_type=message_type,
            subject=subject_generator.get_subject_text()
        )
        message_receiver.message_content_html = render_to_string(template_name, template_context)
        message_receiver.full_clean()
        translation.activate(current_language)
        return message_receiver

    def filter_old_receivers(self, datetime_obj):
        """
        Filter all :class:`.MessageReceivers` created before the given
        `datetime_obj`-argument.
        """
        return self.filter(created_datetime__lt=datetime_obj)


class MessageReceiver(models.Model):
    """
    This class represents a single message to a single user.

    Contains data about the specific message for a user:
        - ForeignKey to a user.
        - The status of the sending.
        - How many time the message has been successfully and unsuccessfully sent to the user.
        - The subject.
        - The content as both html and plaintext.
        - When the message was successfully sent.

    The subject and message-content is stored in the users preferred language when the first
    message was created.

    """
    objects = MessageReceiverQuerySet.as_manager()

    #: When the message receiver was created.
    created_datetime = models.DateTimeField(
        blank=True, null=True, default=timezone.now
    )

    #: Choices for the :obj:`.MessageReceiver.status` field.
    #:
    #: - ``not_sent``: The MessageReceiver has just been created, but not sent yet.
    #: - ``error``: An error occurred when trying to send the message. The status is set to `failed` if the
    #:   :obj:`.sending_failed_count` is greater than the resend limit defined by the
    #:   `DEVILRY_MESSAGE_RESEND_LIMIT`-setting. Error-details and traceback is stored in :obj:`.status_data`.
    #: - ``failed``: The message failed, same as `error`, but the status is set to `failed` if the
    #:   :obj:`.sending_failed_count` is less than or equal to the resend limit defined by the
    #:   `DEVILRY_MESSAGE_RESEND_LIMIT`-setting. Error-details and traceback is stored in :obj:`.status_data`.
    #: - ``sent``: The message was sent to a backend (mailserver, SMS-provider etc.) without any errors.
    #:
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='not_sent',
                                 label=gettext_lazy('Not sent')),
        choices_with_meta.Choice(value='failed',
                                 label=gettext_lazy('Failed')),
        choices_with_meta.Choice(value='error',
                                 label=gettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=gettext_lazy('Sent'))
    )

    #: The status of the message.
    #: Must be one of the choices defined in :obj:`~.MessageReceiver.STATUS_CHOICES`.
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES.iter_as_django_choices_short(),
        default=STATUS_CHOICES.NOT_SENT.value
    )

    #: Extra data for the :obj:`~.MessageReceiver.status` as JSON. Typically used to
    #: save responses from the APIs used to send the message, especially
    #: error responses.
    status_data = models.JSONField(null=False, blank=True, default=dict)

    #: Extra metadata for the message receiver as JSON. This can be anything.
    metadata = models.JSONField(null=False, blank=True, default=dict)

    #: The subject of the message.
    #:
    #: Only used for emails.
    subject = models.CharField(
        max_length=255,
        null=False, blank=True,
        default='')

    #: Message content plain text.
    #:
    #: If :attr:`.MessageReceiver.message_content_html` is set, the HTML
    #: content is converted to plaint text and saved on this field.
    message_content_plain = models.TextField(
        null=False, blank=True, default='')

    #: Message content HTML.
    #:
    #: Optional, but normally used when sending an email.
    message_content_html = models.TextField(
        null=False, blank=True, default='')

    #: The :class:`.BaseMessage` this message receiver belongs too.
    message = models.ForeignKey(
        to=Message,
        on_delete=models.CASCADE
    )

    #: The message type.
    #: Will always be one of the message types in the :obj:`.BaseMessage.message_types`
    #: list of the :obj:`~.MessageReceiver.message`.
    message_type = models.CharField(max_length=30, db_index=True)

    #: The receivers email-address. A user can have multiple email-addresses, this is
    #: the actual address for the `user` the mail was sent/will be sent to.
    send_to = models.CharField(max_length=255, null=False, blank=True, default='')

    #: The User to send this to. Currently we only send
    #: to registered users, so this field is required.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    #: The datetime the message was successfully sent
    #: to the user.
    sent_datetime = models.DateTimeField(null=True, blank=True)

    #: Number of failed attempts.
    sending_failed_count = models.IntegerField(
        default=0
    )

    #: Number of successful attempts.
    sending_success_count = models.IntegerField(
        default=0
    )

    def _send_email(self):
        """
        Sends the email via `devilry.utils.devilry_email.send_message`.

        DO NOT call this method directly.
        """
        send_message(self.subject, self.message_content_html, *[self.user], is_html=True)

    def send(self):
        """
        Simply sends a message to this receiver. This method can also be
        used to resend an email.
        """
        try:
            self._send_email()
            self.sent_datetime = timezone.now()
            self.status = self.STATUS_CHOICES.SENT.value
            self.sending_success_count += 1
            self.save()
        except Exception as exception:
            self.sending_failed_count += 1

            if self.sending_failed_count > settings.DEVILRY_MESSAGE_RESEND_LIMIT:
                self.status = self.STATUS_CHOICES.ERROR.value
            else:
                self.status = self.STATUS_CHOICES.FAILED.value

            if 'errors' in self.status_data:
                self.status_data['errors'].append({
                    'error_message': str(exception),
                    'timestamp': timezone.now().isoformat(),
                    'exception_traceback': traceback.format_exc()
                })
            else:
                self.status_data = {
                    'errors': [{
                        'error_message': str(exception),
                        'timestamp': timezone.now().isoformat(),
                        'exception_traceback': traceback.format_exc()
                    }]
                }
            self.save()

    def clean_message_content_fields(self):
        """
        If :obj:`.BaseMessage.message_content_html` has content and :obj:`.BaseMessage.message_content_plain`
        has not, convert the HTML-content to plaintext and set it on the `message_content_plain`-field.
        """
        if self.message_content_html and not self.message_content_plain:
            self.message_content_plain = emailutils.convert_html_to_plaintext(self.message_content_html).strip()

    def clean_message_type(self):
        """
        Sets `email` as default message type if empty or `None`.
        """
        if not self.message_type:
            self.message_type = 'email'

    def clean(self):
        self.subject = self.subject.strip()
        self.clean_message_type()
        self.clean_message_content_fields()
        self.message_content_plain = self.message_content_plain.strip()

    def __str__(self):
        return '{}'.format(self.user)
