from . import container


class EscapedText(container.AbstractContainerRenderable):
    """
    Renders provided text after escaping any HTML.

    Can not have children.
    """

    template_name = "django_cradmin/uicontainer/text/escaped_text.django.html"

    def __init__(self, text, **kwargs):
        """
        Args:
            text: The text to render.
            **kwargs: Kwargs for :class:`~django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self.text = text
        super(EscapedText, self).__init__(**kwargs)

    @property
    def can_have_children(self):
        return False


class Html(container.AbstractContainerRenderable):
    """
    Renders provided HTML directly without any formatting or escaping.

    Can not have children.
    """

    template_name = "django_cradmin/uicontainer/text/html.django.html"

    def __init__(self, html=None, **kwargs):
        """
        Args:
            html: The HTML to render.
            **kwargs: Kwargs for :class:`~django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self._overridden_html = html
        super(Html, self).__init__(**kwargs)

    @property
    def can_have_children(self):
        return False

    def get_default_html(self):
        """
        Get the default HTML to render if no HTML is provided
        as the ``html`` kwarg for :meth:`.__init__`.

        Defaults to empty string.
        """
        return ""

    @property
    def html(self):
        return self._overridden_html or self.get_default_html()
