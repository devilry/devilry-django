import typing

from django.conf import settings
from django.utils.module_loading import import_string

if typing.TYPE_CHECKING:
    from devilry.devilry_account.models import User


class ErrorReporter:
    def __init__(
        self, context, message: str, exception: typing.Optional[Exception] = None, user: typing.Optional["User"] = None
    ) -> None:
        self.context = context
        self.message = message
        self.exception = exception
        self.user = user

    def report(self) -> None:
        """
        Reports an error message to the logging system and/or some external system.

        The default implementation logs the error using Python's logging module,
        but this can be overridden by subclassing and providing a different implementation
        and specifying the custom class as a string path in the DEVILRY_ERROR_REPORTER_CLASS setting.
        """
        import logging

        logger = logging.getLogger(self.context)
        if self.exception is None:
            logger.error(self.message)
        else:
            logger.exception(self.message)


class SentryErrorReporter(ErrorReporter):
    """
    Reports errors to Sentry.

    Does not send the message to logs.
    """

    send_message_to_logs = False

    def report(self) -> None:
        """
        Reports an error message to Sentry.
        """
        import logging

        import sentry_sdk

        if self.send_message_to_logs:
            logger = logging.getLogger(self.context)
            logger.error(self.message)

        sentry_sdk.set_extra("devilry_context", self.context)
        if self.user:
            sentry_sdk.set_user(
                {
                    "id": self.user.pk,
                    "username": self.user.shortname,
                }
            )
        if self.exception is None:
            sentry_sdk.capture_message(self.message, level="error")
        else:
            sentry_sdk.capture_exception(self.exception)


class SentryWithLogsErrorReporter(SentryErrorReporter):
    """
    Same as SentryErrorReporter, but also sends the message to logs.

    Does not send the exception traceback to logs, only the message.
    """

    send_message_to_logs = True


def report_devilry_error(
    context, message: str, exception: typing.Optional[Exception] = None, user: typing.Optional["User"] = None
) -> None:
    """
    Reports an error message to the logging system.
    """
    reporter_class_path = getattr(settings, "DEVILRY_ERROR_REPORTER_CLASS", None)
    if reporter_class_path:
        ReporterClass = import_string(reporter_class_path)
    else:
        ReporterClass = ErrorReporter
    reporter = ReporterClass(context=context, message=message, exception=exception, user=user)
    reporter.report()


class FakeException(Exception):
    pass


def debug_error_trigger(user, context=None):
    """
    Function to trigger an error for testing error reporting.

    Raises a FakeException if the provided user has `user.shortname` in the
    `DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES` setting.

    Example setup in `settings.py`::

        DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES = ['thefirstsuperuser', 'theothersuperuser']

    """
    trigger_shortnames = getattr(settings, "DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES", None)
    if not trigger_shortnames:
        return
    if not user or not user.is_authenticated:
        return

    if user.shortname in trigger_shortnames:
        errormessage = (
            f"Debug error triggered for testing error reporting because {user.shortname} is in "
            f"the DEVILRY_DEBUG_ERROR_TRIGGER_USER_SHORTNAMES setting."
        )
        if context:
            errormessage += f" Context info: {context}"
        raise FakeException(errormessage)
