from . import form_mixins
from . import container


class BaseHelpTextRenderable(container.AbstractContainerRenderable, form_mixins.FieldWrapperRenderableChildMixin):
    """
    Base class for renderers of help text for a
    :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`.

    You never use this on its own outside a
    :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`.
    """

    def get_default_bem_block_or_element(self):
        return "help-text"


class AutomaticHelpText(BaseHelpTextRenderable):
    """
    Renders help text for a :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`
    using the help text from the Django form field.

    You never use this on its own outside a
    :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`.
    """

    template_name = "django_cradmin/uicontainer/field_help_text/automatic_help_text.django.html"

    def get_default_html_tag(self):
        return "p"

    @property
    def help_text(self):
        """
        Get the help text configured for the form field.

        Can be overridden to provide a custom help text.
        """
        bound_formfield = self.field_wrapper_renderable.bound_formfield
        return bound_formfield.help_text

    @property
    def should_render(self):
        """
        Returns ``False`` if :meth:`.help_text` is empty,
        which means that the help text is not rendered at all if
        there is no help text.
        """
        return bool(self.help_text)
