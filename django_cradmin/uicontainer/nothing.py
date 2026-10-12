from . import container


class Nothing(container.AbstractContainerRenderable):
    """
    Does not render anything.

    Useful in cases where you do not want to render anything.
    We use this instead of ``None`` to avoid having to handle
    ``None`` values everywhere.

    Typical use case is the help_text_renderable kwarg for
    :class:`django_cradmin.uicontainer.field.FieldWrapper`.
    If you want to disable the help text, you can not set the kwarg
    to ``None``, because that would just fall back to using the
    default help text renderable, so you use class instead.
    """

    @property
    def should_render(self):
        return False
