# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import translation

from django_cradmin.apps.cradmin_email import emailutils

from ievv_opensource.utils import choices_with_meta

from devilry.devilry_email.utils import activate_translation_for_user
from devilry.utils.devilry_email import send_message


class Message(models.Model):
    """
    A message that contains a message sent via different message types (SMS or E-mail).
    """
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
                                 label=ugettext_lazy('Draft')),
        choices_with_meta.Choice(value='preparing',
                                 label=ugettext_lazy('Preparing for sending'),
                                 description=ugettext_lazy('Building the list of actual users to send to.')),
        choices_with_meta.Choice(value='sending',
                                 label=ugettext_lazy('Sending')),
        choices_with_meta.Choice(value='error',
                                 label=ugettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=ugettext_lazy('Sent'))
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
    status_data = JSONField(null=False, blank=True, default=dict)

    #: Extra metadata for the message receiver as JSON. This can be anything.
    metadata = JSONField(null=False, blank=True, default=dict)

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
        choices_with_meta.Choice(value='other'),
        choices_with_meta.Choice(value='comment_delivery'),
        choices_with_meta.Choice(value='deadline_moved'),
        choices_with_meta.Choice(value='feedback'),
        choices_with_meta.Choice(value='feedback_updated')
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
    #: - ``['email']`` - Send as email only
    message_type = ArrayField(
        models.CharField(max_length=30),
        blank=False, null=False
    )

    #: :class:`.MessageReceiver`s are created for this message
    #: based on the content of this field.
    #:
    #: Each subclass defines how the dataformat of this field should be.
    #: Override :meth:`prepare_message_receivers` to create message receivers from this field.
    virtual_message_receivers = JSONField(
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
            message_receiver = MessageReceiver.objects.create(
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

                for message_receiver in self.messagereceiver_set.all():
                    message_receiver.send()

                # Set status to 'sent'.
                self.status = self.STATUS_CHOICES.SENT.value
                self.save()
            except Exception as exception:
                self.status = self.STATUS_CHOICES.ERROR.value
                self.status_data = {
                    'error_message': str(exception),
                    'exception_traceback': traceback.format_exc()
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

    def __unicode__(self):
        return 'Message - {} - {}'.format(self.context_type, self.created_datetime)


class MessageReceiverQuerySet(models.QuerySet):
    def create(self, user, message, message_type, subject_generator, template_name, template_context):
        """
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


class MessageReceiver(models.Model):
    """
    A message receiver for a subclass of :class:`.BaseMessage`.
    """
    objects = MessageReceiverQuerySet.as_manager()

    #: Choices for the :obj:`.MessageReceiver.status` field.
    #:
    #: - ``not_sent``: The MessageReceiver has just been created, but not sent yet.
    #: - ``error``: There is some error with this message. Details about the error(s)
    #:   is available in :obj:`.status_data`.
    #: - ``sent``: Sent to the backend. We do not know if it was successful or
    #:   not yet when we have this status (E.g.: We do not know if the message has been received, but
    #:   we are waiting for an update that tells us if it was).
    #:   Backends that do not support reporting if messages was sent successfully
    #:   or not will only use this status, not the ``received`` status.
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='not_sent',
                                 label=ugettext_lazy('Not sent')),
        choices_with_meta.Choice(value='error',
                                 label=ugettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=ugettext_lazy('Sent'))
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
    status_data = JSONField(null=False, blank=True, default=dict)

    #: Extra metadata for the message receiver as JSON. This can be anything.
    metadata = JSONField(null=False, blank=True, default=dict)

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

    #: The datetime the message was sent to this user.
    sent_datetime = models.DateTimeField(null=True, blank=True)

    def send(self):
        """
        Simply sends a message to this receiver. This method can also be
        used to resend an email.
        """
        with transaction.atomic():
            try:
                send_message(self.subject, self.message_content_html, *[self.user], is_html=True)
                self.sent_datetime = timezone.now()
                self.status = self.STATUS_CHOICES.SENT.value
                self.save()
            except Exception as exception:
                self.status = self.STATUS_CHOICES.ERROR.value
                self.status_data = {
                    'error_message': str(exception),
                    'exception_traceback': traceback.format_exc()
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
            self.message_type = ['email']

    def clean(self):
        self.subject = self.subject.strip()
        self.clean_message_type()
        self.clean_message_content_fields()
        self.message_content_plain = self.message_content_plain.strip()

    def __unicode__(self):
        return '{}'.format(self.user)
