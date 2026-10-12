import json
from xml.sax.saxutils import quoteattr

from crispy_forms import layout
from django.utils.translation import pgettext_lazy

from cradmin_legacy import renderable
from cradmin_legacy.crispylayouts import PrimarySubmitBlock, CradminFormHelper
from cradmin_legacy.viewhelpers.listfilter.base import abstractfilterlistchild


class Target(renderable.AbstractRenderableWithCss, abstractfilterlistchild.FilterListChildMixin):
    """
    Renders a multiselect target form.

    If you have multiple lists with multiselect2 on the same page,
    you have to ensure the DOM IDs are unique by overriding :meth:`.get_dom_id`.
    """

    #: The template used to render this renderable.
    template_name = "cradmin_legacy/viewhelpers/multiselect2/target_renderer/target.django.html"

    #: The default for :meth:`.~Target.get_dom_id`.
    default_target_dom_id = "cradmin_legacy_multiselect2_select_target"

    #: Used to add custom attributes like angularjs directives to the form.
    #: See :meth:`.get_form_attributes`.
    form_attributes = {}

    def __init__(
        self,
        form,
        dom_id=None,
        without_items_text=None,
        with_items_title=None,
        no_items_selected_text=None,
        submit_button_text=None,
        form_action=None,
        empty_selection_allowed=False,
    ):
        """
        Args:
            form: A django Form object.
            dom_id: See :meth:`.get_dom_id`.
            without_items_text: See :meth:`.get_without_items_text`.
            no_items_selected_text: See :meth:`.get_no_items_selected_text`.
            with_items_title: See :meth:`.get_with_items_title`.
            submit_button_text: See :meth:`.get_submit_button_text`.
            form_action: See :meth:`.get_form_action`.
        """
        self.form = form
        self.dom_id = dom_id
        self.without_items_text = without_items_text
        self.with_items_title = with_items_title
        self.no_items_selected_text = no_items_selected_text
        self.submit_button_text = submit_button_text
        self.form_action = form_action
        self.empty_selection_allowed = empty_selection_allowed

    def get_dom_id(self):
        """
        Returns:
            str: The DOM id of the form wrapping everything rendered by this renderable.

            Defaults to the ``dom_id`` parameter for ``__init__`` falling back on
            :obj:`.default_target_dom_id`.
        """
        if self.dom_id:
            return self.dom_id
        else:
            return self.default_target_dom_id

    def get_with_items_title(self):
        """
        Returns:
            str: The title of the box when there are items selected.

            Defaults to the ``with_items_title`` parameter for ``__init__``,
            falling back on ``"Selected items"`` (translatable).
        """
        if self.with_items_title:
            return self.with_items_title
        else:
            return pgettext_lazy("multiselect2 target renderer", "Selected items")

    def get_submit_button_text(self):
        """
        This is used in :meth:`.get_buttons`, so if you override that or :meth:`.get_button_layout`,
        this is not used.

        Returns:
            str: The submit button text.

            Defaults to the ``submit_button_text`` parameter for ``__init__``,
            falling back on ``"Submit selection"`` (translatable).
        """
        if self.submit_button_text:
            return self.submit_button_text
        else:
            return pgettext_lazy("multiselect2 target renderer", "Submit selection")

    def get_without_items_text(self):
        """
        Returns:
            str: The text to show when there are no items selected and :meth:`.get_empty_selection_allowed`
            returns ``False``.

            Defaults to the ``without_items_text`` parameter for ``__init__``,
            falling back on empty string.
        """
        if self.without_items_text:
            return self.without_items_text
        else:
            return ""

    def get_empty_selection_allowed(self):
        """
        Returns:
            bool: If no selected items is allowed, this should return ``True``.
            Returns the value of the ``empty_selection_allowed`` parameter
            for ``__init__`` by default.
        """
        return self.empty_selection_allowed

    def get_no_items_selected_text(self):
        """
        Returns:
            str: The text to show when there are no items selected and :meth:`.get_empty_selection_allowed`
            returns ``True``.

            Defaults to the ``no_items_selected_text`` parameter for ``__init__``,
            falling back on ``"(None)"``.
        """
        if self.no_items_selected_text:
            return self.no_items_selected_text
        else:
            return pgettext_lazy("multiselect2 target renderer", "(None)")

    def get_form_action(self, request):
        """
        If you override this, you should also override
        :meth:`.post_url_as_it_is_when_form_is_submitted` and return ``False``.

        Args:
            request: An HttpRequest object.

        Returns:
            str: The ``<form>`` action attribute value.

            Defaults to the ``form_action`` parameter for ``__init__``,
            falling back on ``request.get_full_path()``.
        """
        if self.form_action:
            return self.form_action
        else:
            return request.get_full_path()

    def post_url_as_it_is_when_form_is_submitted(self):
        """
        If this returns ``True`` (the default), the ``action``-attribute of the
        form will be updated to match the URL in the browser when the form
        is submitted.

        This defaults to ``True`` unless you set :obj:`.form_action`.

        The primary reason for this feature is here is for javascript libraries
        that update the URL. It is usually a bad user experience to reset their
        choices (filters, search, etc.) when they post their selection.
        """
        if self.form_action:
            return False
        else:
            return True

    def get_angularjs_directive_dict(self):
        """
        Get options for the ``cradmin-legacy-multiselect2-target`` angularjs
        directive.

        Returns:
            dict: With options for the directive.
        """
        return {
            "updateFormActionToWindowLocation": self.post_url_as_it_is_when_form_is_submitted(),
        }

    def get_angularjs_directive_json(self):
        """
        JSON encode :meth:`.get_angularjs_directive_dict`.

        Returns:
            str: The return value of :meth:`.get_select_directive_dict`
            as a json encoded and xml attribute encoded string.
        """
        return quoteattr(json.dumps(self.get_angularjs_directive_dict()))

    def get_context_data(self, request=None):
        context = super().get_context_data(request=request)
        context["form_action"] = self.get_form_action(request=request)
        context["angularjs_directive_json"] = self.get_angularjs_directive_json()
        return context

    def get_field_layout(self):
        """
        Get a list/tuple of fields. These are added to a ``crispy_forms.layout.Layout``.

        Must be overridden.

        Simple example::

            from cradmin_legacy.viewhelpers import multiselect2view
            from crispy_forms import layout

            class MyMultiselect2View(multiselect2view.ListbuilderView):
                # ... other required stuff

                def get_field_layout(self):
                    return [
                        'name',
                        layout.Field('age', css_class="the-name")
                    ]
        """
        return []

    def get_hidden_fields(self):
        """
        Get hidden fields for the form.

        Returns:
            An iterable of :class:`crispy_forms.layout.Hidden` objects.
            Defaults to an empty list.
        """
        return []

    def get_buttons(self):
        """
        Get buttons for the form, normally one or more submit button.

        Each button must be a crispy form layout object, typically some
        subclass of :class:`crispy_forms.layout.Submit`.

        The default is::

            from cradmin_legacy.crispylayouts import PrimarySubmitBlock

            return [
                PrimarySubmitBlock('save', self.get_submit_button_text()),
            ]

        .. seealso:: This method is used by :meth:`.get_button_layout`.
            The default label is returned by :meth:`.get_submit_button_text`.
        """
        return [
            PrimarySubmitBlock("save", self.get_submit_button_text()),
        ]

    def get_button_layout(self):
        """
        Get the button layout. This is added to the crispy form layout.

        You will normally want to override :meth:`.get_buttons` instead of this
        method.

        Defaults to a :class:`crispy_forms.layout.Div` with css class
        ``cradmin-legacy-multiselect2-target-submitbuttons`` containing all the buttons
        returned by :meth:`.get_buttons`.
        """
        return [layout.Div(*self.get_buttons(), css_class="cradmin-legacy-multiselect2-target-submitbuttons")]

    def get_formhelper_class(self):
        return CradminFormHelper

    def get_formhelper(self):
        """
        Get a :class:`crispy_forms.helper.FormHelper`.

        You normally do not need to override this directly. Instead
        you should override:

        - :meth:`.get_field_layout`.
        - :meth:`.get_hidden_fields`
        - :meth:`.get_buttons` (or perhaps :meth:`.get_button_layout`)
        """
        helper = self.get_formhelper_class()()
        layoutargs = list(self.get_field_layout()) + list(self.get_button_layout()) + list(self.get_hidden_fields())
        helper.layout = layout.Layout(*layoutargs)
        helper.form_tag = False
        return helper


class ManyToManySelectTarget(Target):
    """
    Renders a multiselect target form for
    :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.
    """

    def __init__(self, target_formfield_id, *args, **kwargs):
        """
        Args:
            target_formfield_id: The DOM ID of the target form field.
        """
        self.target_formfield_id = target_formfield_id
        super().__init__(*args, **kwargs)

    def get_usethis_directive_dict(self):
        return {"fieldid": self.target_formfield_id}

    def get_usethis_directive_json(self):
        return json.dumps(self.get_usethis_directive_dict())

    def get_buttons(self):
        return [
            PrimarySubmitBlock(
                "usethis",
                self.get_submit_button_text(),
                cradmin_legacy_multiselect2_use_this=self.get_usethis_directive_json(),
            ),
        ]
