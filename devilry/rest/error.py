class RestError(Exception):
    """
    Base class for REST errors.
    """
    def __init__(self, i18nkey, **i18nparameters):
        """
        :param i18nkey: Should be a translation key for
            ``devilry.i18n``, however it may be an error message if the error is
            not ment to be displayed to normal users user.
        :param i18nparameters: Arguments that is passed into the translation string.
        """
        self.i18nkey = i18nkey
        self.i18nparameters = i18nparameters

    def __unicode__(self):
        return self.i18nkey

class ClientErrorBase(RestError):
    """
    Base class for HTTP 4XX errors. The error messages produced by these
    exceptions are considered safe to forward to the client.

    When you subclass these exceptions, you should provide a ``__unicode__``
    method that returns an error message that can be displayed to the user.

    .. attribute:: STATUS

        The HTTP status code to respond with. Defaults to ``400``, however
        subclasses my override this.
    """
    STATUS = 400

class MethodNotAllowed(ClientErrorBase):
    """
    A request was made of a resource using a request method not supported by that
    resource; for example, using GET on a form which requires data to be
    presented via POST, or using PUT on a read-only resource.
    """

class BadRequestError(ClientErrorBase):
    """
    The request cannot be fulfilled due to bad syntax.
    """

class BadRequestFieldError(BadRequestError):
    """
    Bad request error containing a ``fieldname`` as metadata.
    """
    def __init__(self, fieldname, i18nkey, **i18nparameters):
        super(BadRequestError, self).__init__(i18nkey, **i18nparameters)
        self.fieldname = fieldname

class ForbiddenError(ClientErrorBase):
    """
    The request was a legal request, but the server is refusing to respond to
    it due to lacking permissions.
    """
    STATUS = 403

class NotFoundError(ClientErrorBase):
    """
    404 not found
    """
    STATUS = 404

class NotAcceptable(ClientErrorBase):
    """
    The requested resource is only capable of generating content not acceptable
    according to the Accept headers sent in the request.
    """
    STATUS = 406

class InvalidInputContentTypeError(NotAcceptable):
    """
    Unsupported input content type. There is no HTTP code for this, however
    since we default to falling back on the ACCEPT header, it is natural to use
    406.
    """
