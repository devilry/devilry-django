from django.utils.translation import pgettext_lazy

from cradmin_legacy import renderable


class SelectedItem(renderable.AbstractRenderableWithCss):
    """
    Renders a selected item. This is rendered by
    :class:`cradmin_legacy.viewhelpers.multiselect2.listbuilder_itemvalues.ItemValue`,
    and added to a :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
    when the "select"-button in the ItemValue is clicked.
    """

    #: The template used to render this selected item.
    template_name = "cradmin_legacy/viewhelpers/multiselect2/selected_item_renderer/selected-item.django.html"

    #: If this is specified, we will add an attribute with this name
    #: for the value as an attribute of the object.
    #:
    #: I.e.: if ``valuealias = "person"``, you will be able to use ``me.person`` in
    #: the template, and you will be able to use ``self.person`` in any methods you
    #: add or override in the class (just remember to call ``super()`` if you override
    #: ``__init__``).
    valuealias = None

    def __init__(self, value):
        """
        Args:
            value: The value to render. Typically a django model object.

        """
        self.value = value
        if self.valuealias:
            setattr(self, self.valuealias, self.value)

    def get_base_css_classes_list(self):
        return ["cradmin-legacy-multiselect2-selected-item"]

    def get_title(self):
        """
        Returns:
            str: The title of the selected item.
        """
        return str(self.value)

    def get_description(self):
        """
        Returns:
            str: The description of the selected item.

            This is shown below the title. It defaults to ``None``,
            which means that no description is rendered.
        """
        return None

    def get_deselectbutton_text(self):
        """
        Returns:
            str: The text for the deselect button.

            Defaults to the ``deselectbutton_text`` parameter for ``__init__``,
            falling back on ``"Deselect"`` (translatable).
        """
        return pgettext_lazy("multiselect2 deselect button", "Deselect")

    def get_deselectbutton_aria_label(self):
        """
        Returns:
            str: The text for the aria-label of the deselect button.

            Defaults to ``"Deselect <self.get_title()>"`` (translatable).
        """
        return pgettext_lazy("multiselect2 deselect button", 'Deselect "%(title)s"') % {"title": self.get_title()}

    def get_deselect_button_base_cssclasses_list(self):
        """
        Get the list of base css classes to use for the deselect button.
        You normally do not want to override this. Override
        :meth:`.get_deselect_button_extra_cssclasses_list` instead.
        """
        return ["cradmin-legacy-multiselect2-target-selected-item-deselectbutton"]

    def get_deselect_button_extra_cssclasses_list(self):
        """
        Get the list of extra css classes to use for the deselect button.

        Defaults to ``['btn', 'btn-default']``.
        Override this to provide your own css classes.
        """
        return [
            "btn",
            "btn-default",
        ]

    def get_deselect_button_cssclasses_list(self):
        """
        Get the list of css classes to use for the deselect button.

        You normally do not want to override this. Override
        :meth:`.get_deselect_button_extra_cssclasses_list` instead.
        """
        return ["btn", "btn-default", "cradmin-legacy-multiselect2-target-selected-item-deselectbutton"]

    def get_deselect_button_cssclasses_string(self):
        css_classes = self.get_deselect_button_base_cssclasses_list() + self.get_deselect_button_extra_cssclasses_list()
        return " ".join(css_classes)

    def get_inputfield_name(self):
        """
        Returns:
            str: The name of the input field.

            Defaults to the ``inputfield_name`` parameter for ``__init__``, falling
            back on ``selected_items``.
        """
        return "selected_items"

    def get_inputfield_value(self):
        """
        Returns:
            str or int: The value to put in the ``value`` attribute of the input field.
        """
        return self.value.pk
