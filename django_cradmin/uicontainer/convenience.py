from . import container


class AbstractWithOptionalEscapedText(container.AbstractContainerRenderable):
    """
    A renderable that has an optional ``text`` kwarg
    that adds the provided text as a :class:`django_cradmin.uicontainer.text.EscapedText`
    child.
    """

    def __init__(self, text=None, **kwargs):
        """
        Args:
            text: Optional text to add to the container. See :meth:`.prepopulate_children_list`.
            **kwargs: Kwargs for :class:`~django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self.text = text
        super(AbstractWithOptionalEscapedText, self).__init__(**kwargs)

    def prepopulate_children_list(self):
        """
        Automatically adds a :class:`django_cradmin.uicontainer.text.EscapedText`
        child if the ``text`` kwarg for :meth:`.__init__` is set to a value
        that is ``bool(text) == True``.
        """
        from . import text

        if self.text:
            return [text.EscapedText(text=self.text)]
        else:
            return []


class AbstractWithOptionalParagraphWithEscapedText(container.AbstractContainerRenderable):
    """
    A renderable that has an optional ``text`` kwarg
    that adds the provided text as a :class:`django_cradmin.uicontainer.typography.Paragraph`
    child containing a :class:`django_cradmin.uicontainer.text.EscapedText` child
    """

    def __init__(self, text=None, **kwargs):
        """
        Args:
            text: Optional text to add to the container. See :meth:`.prepopulate_children_list`.
            **kwargs: Kwargs for :class:`~django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self.text = text
        super(AbstractWithOptionalParagraphWithEscapedText, self).__init__(**kwargs)

    def prepopulate_children_list(self):
        """
        Automatically adds a :class:`django_cradmin.uicontainer.typography.Paragraph`
        child with a :class:`django_cradmin.uicontainer.text.EscapedText`
        child if the ``text`` kwarg for :meth:`.__init__` is set to a value
        that is ``bool(text) == True``.
        """
        from . import text
        from . import semantic

        if self.text:
            return [semantic.Paragraph(children=[text.EscapedText(text=self.text)])]
        else:
            return []
