from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import html2text


def convert_html_to_plaintext(html):
    """
    Convert the given ``html`` to plain text.
    """
    return html2text.html2text(html)


class AbstractEmail:
    """
    Abstract class for sending email.

    Examples:

        Simple example::

            from cradmin_legacy.apps.cradmin_email import emailutils

            class SimpleEmail(emailutils.AbstractEmail):
                subject_template = 'myapp/subject.django.txt'
                html_message_template = 'myapp/html_message.django.html'

            SimpleEmail(recipient='test@example.com').send()

        Specify a sender::

            SimpleEmail(recipient='test@example.com', from_email='admin@example.com').send()

        Build a common abstract class that defaults to something other
        than ``settings.DEFAULT_FROM_EMAIL``::

            class AbstractAccountEmail(emailutils.AbstractEmail):
                def get_default_from_email(self):
                    return 'account@example.com'

        Specify a plaintext template instead of converting the HTML email
        to plaintext::

            class WithPlaintextEmail(emailutils.AbstractEmail):
                subject_template = 'myapp/subject.django.txt'
                html_message_template = 'myapp/html_message.django.html'
                plaintext_message_template = 'myapp/plaintext_message.django.txt'

        Set subject via a translation string instead of a template
        (you can do this for the message as well)::

            class StringSubjectEmail(emailutils.AbstractEmail):
                html_message_template = 'myapp/html_message.django.html'

                def render_subject(self):
                    return _('My subject')

        Provide context data for the templates::

            SimpleEmail(recipient='test@example.com', extra_context_data={
                'name': 'Peter Pan',
            }).send()
    """

    #: The Django template for the subject. You must set this in subclasses,
    #: or override :meth:`.get_subject_template` or :meth:`.render_subject`.
    subject_template = None

    #: The Django template for the HTML message. You must set this in subclasses,
    #: or override :meth:`.get_html_message_template` or :meth:`.render_html_message`.
    html_message_template = None

    #: The Django template for the Plain text message.
    #: If this or :meth:`.get_plaintext_message_template` or :meth:`.render_subject`
    #: is not set in subclasses, we autoconvert the HTML message to plain text.
    plaintext_message_template = None

    #: Fallback value of the CRADMIN_LEGACY_EMAIL_DEFAULT_CONTEXT_DATA setting
    #: is not set.
    DEFAULT_CONTEXT_DATA = {
        "body_style": "background-color: #fff;",
        "common_td_style": "font-family: Arial, sans-serif; "
        "font-size: 16px; "
        "line-height: 1.42857143; "
        "margin: 0; "
        "letter-spacing: 0.5px; ",
        "header_td_style": "",
        "logo_style": "",
        "contents_td_style": "padding-top: 20px; padding-bottom: 28px;",
        "footer_td_style": "border-top: 3px solid #eee; "
        "font-size: 13px; "
        "color: #777; "
        "text-align: center; "
        "padding-top: 20px; "
        "padding-bottom: 20px; ",
        "footer_link_style": "color: #777; text-decoration: underline;",
        "link_style": "color: #377CA8; text-decoration: underline;",
        "secondary_button_link_style": "font-size: 16px; "
        "font-family: Arial, sans-serif; "
        "color: #fff; "
        "text-decoration: none; "
        "font-weight: bold; "
        "text-transform: uppercase; "
        "letter-spacing: 1px; "
        "background-color: #999999; "
        "border-top: 10px solid #999999; "
        "border-bottom: 10px solid #999999; "
        "border-right: 16px solid #999999; "
        "border-left: 16px solid #999999; "
        "border-radius: 3px; "
        "-webkit-border-radius: 3px; "
        "-moz-border-radius: 3px; "
        "display: inline-block;",
        "primary_button_link_style": "font-size: 16px; "
        "font-family: Arial, sans-serif; "
        "color: #fff; "
        "text-decoration: none; "
        "font-weight: bold; "
        "text-transform: uppercase; "
        "letter-spacing: 1px; "
        "background-color: #377CA8; "
        "border-top: 10px solid #377CA8; "
        "border-bottom: 10px solid #377CA8; "
        "border-right: 16px solid #377CA8; "
        "border-left: 16px solid #377CA8; "
        "border-radius: 3px; "
        "-webkit-border-radius: 3px; "
        "-moz-border-radius: 3px; "
        "display: inline-block;",
    }

    def get_subject_template(self):
        """
        Alternative way to specify :obj:`.subject_template`.
        This takes presedence over :obj:`.subject_template`.
        """
        if self.subject_template:
            return self.subject_template
        else:
            raise NotImplementedError("You must override subject_template or get_subject_template")

    def get_html_message_template(self):
        """
        Alternative way to specify :obj:`.html_message_template`.
        This takes presedence over :obj:`.html_message_template`.
        """
        if self.html_message_template:
            return self.html_message_template
        else:
            raise NotImplementedError("You must override html_message_template or get_html_message_template")

    def get_plaintext_message_template(self):
        """
        Alternative way to specify :obj:`.plaintext_message_template`.
        This takes presedence over :obj:`.plaintext_message_template`.
        """
        return self.plaintext_message_template

    def get_subject_prefix(self):
        """
        Get the prefix to use for the subject.

        Defaults to ``settings.CRADMIN_LEGACY_EMAIL_SUBJECT_PREFIX``, falling
        back to empty string.

        If your privide a prefix, you should most likely include an empty
        space at the end of it.
        """
        if hasattr(settings, "CRADMIN_LEGACY_EMAIL_SUBJECT_PREFIX"):
            return settings.CRADMIN_LEGACY_EMAIL_SUBJECT_PREFIX
        else:
            return ""

    def render_subject(self):
        """
        Render the subject. You can override this if you want to
        adjust template rendering or avoid using a template.
        """
        subject = render_to_string(self.get_subject_template(), self.get_context_data()).strip()
        return f"{self.get_subject_prefix()}{subject}"

    def render_html_message(self):
        """
        Render the html message. You can override this if you want to
        adjust template rendering or avoid using a template.
        """
        return render_to_string(self.get_html_message_template(), self.get_context_data())

    def __get_rendered_html_message(self):
        """
        We use this internally to avoid rendering the html message
        twice for the default case where the plaintext message is
        created from the HTML message.
        """
        if not hasattr(self, "_rendered_html_message"):
            self._rendered_html_message = self.render_html_message().strip()
        return self._rendered_html_message

    def render_plaintext_message(self):
        """
        Render the plaintext message. You can override this if you want to
        adjust template rendering or avoid using a template.

        If no :obj:`.plaintext_message_template` or :meth:`.get_plaintext_message_template`
        is specified, we convert the HTML message to plaintext using
        :func:`.convert_html_to_plaintext`.
        """
        template_name = self.get_plaintext_message_template()
        if template_name:
            return render_to_string(template_name, self.get_context_data()).strip()
        else:
            return convert_html_to_plaintext(self.__get_rendered_html_message())

    def get_default_context_data(self):
        """
        Get the default context data.

        You should normally not override this, but rather use it if you override
        :meth:`.get_context_data` and calling ``super().get_context_data()``
        is not a suitable solution.
        """
        context_data = {
            "from_email": self.from_email,
            "CRADMIN_LEGACY_SITENAME": getattr(settings, "CRADMIN_LEGACY_SITENAME", ""),
            "CRADMIN_LEGACY_EMAIL_LOGO_HTML": getattr(settings, "CRADMIN_LEGACY_EMAIL_LOGO_HTML", ""),
        }
        if hasattr(settings, "CRADMIN_LEGACY_EMAIL_DEFAULT_CONTEXT_DATA"):
            context_data.update(settings.CRADMIN_LEGACY_EMAIL_DEFAULT_CONTEXT_DATA)
        else:
            context_data.update(self.DEFAULT_CONTEXT_DATA)
        return context_data

    def get_context_data(self):
        """
        Get the template context data sent to :obj:`.subject_template`,
        :obj:`.html_message_template` and :obj:`.plaintext_message_template`.

        By default this returns:

        - ``from_email``.
        - ``CRADMIN_LEGACY_SITENAME`` (if set as a Django setting).
        - anything you send as the ``extra_context_data`` argument to the constructor.
        - Anything in the ``CRADMIN_LEGACY_EMAIL_DEFAULT_CONTEXT_DATA`` setting.
        """
        context_data = self.get_default_context_data()
        if self.extra_context_data:
            context_data.update(self.extra_context_data)
        return context_data

    def get_from_email(self):
        """
        Get the email address of the sender. Override this
        if you want to provide the ``from_email`` as a method
        instead of argument to the constructor.
        """
        if self.from_email:
            return self.from_email
        else:
            raise NotImplementedError("You must send from_email as argument to __init__, or override get_from_email().")

    def get_recipient_list(self):
        """
        Get the list of recipients. Override this
        if you want to provide the ``recipient_list`` as a method
        instead of argument to the constructor.
        """
        if self.recipient_list:
            return self.recipient_list
        else:
            raise NotImplementedError(
                "You must send recipient_list or recipient as argument to __init__, or override get_recipient_list()."
            )

    def get_send_mail_kwargs(self):
        """
        Get a dict with kwargs for :meth:`django.core.mail.send_mail`.

        We default to building this from the various methods on this class,
        but you can override this to adjust the kwargs.
        """
        return {
            "subject": self.render_subject(),
            "message": self.render_plaintext_message(),
            "html_message": self.__get_rendered_html_message(),
            "from_email": self.get_from_email(),
            "recipient_list": self.get_recipient_list(),
        }

    def send(self):
        """
        Send the email.
        """
        send_mail(**self.get_send_mail_kwargs())

    def get_default_from_email(self):
        """
        Get the fallback value for ``from_email``. Defaults to
        ``settings.DEFAULT_FROM_EMAIL``, but you can override this
        to provide a common superclass that defaults to sending
        from a different address.
        """
        return settings.DEFAULT_FROM_EMAIL

    def __init__(self, recipient=None, recipient_list=None, extra_context_data=None, from_email=None):
        """
        Parameters:
            recipient (str): The recipient of the email.
            recipient_list (list): The recipients of the email. Use this instead of ``recipient``
                if you want to send the message to multiple people.
            extra_context_data (dict): An optional dict with extra context data for the templates.
            from_email: The email address we send the message from.
                Defaults to :meth:`.get_default_from_email`.
        """
        if recipient and recipient_list:
            raise ValueError("You can only specify one of recipient or recipient_list.")
        if recipient:
            self.recipient_list = [recipient]
        else:
            self.recipient_list = recipient_list

        if from_email:
            self.from_email = from_email
        else:
            self.from_email = self.get_default_from_email()

        self.extra_context_data = extra_context_data
