from django.utils.translation import gettext_lazy, pgettext, pgettext_lazy

from cradmin_legacy.viewhelpers.listfilter.base.abstractfilter import AbstractFilter


class AbstractInputFilter(AbstractFilter):
    """
    Abstract base class for any filter that uses a single text input field.
    """

    template_name = "cradmin_legacy/viewhelpers/listfilter/django/single/textinput/base.django.html"

    #: The text used in URLs as placeholder for the value of this filter.
    #: The AngularJS directive replaces this with the actual value.
    #: You should not have to override this.
    urlpattern_replace_text = "_-_TEXTINPUT_-_VALUE_-_"

    def get_input_html_element_type(self):
        """
        Get the ``type``-attribute of the input HTML element.

        Defaults to ``"text"``.
        """
        return "text"

    def get_input_html_element_pattern(self):
        """
        Get the ``pattern`` attribute of the input HTML element.

        Defaults to ``None``. If this returns a value that
        is ``bool(value) == False``, the pattern attribute is
        not added to the input HTML element.
        """
        return None

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listfilter-filter-single-input")
        return css_classes

    def get_placeholder(self):
        """
        Get the placeholder text for the input element.

        Defaults to empty string.
        """
        return ""

    def get_inputfield_value(self):
        return self.get_cleaned_value() or ""

    def get_urlpattern(self):
        """
        Get the URL pattern to use when the input value is a non-empty string.

        You should not need to override this.
        """
        return self.build_set_values_url(values=[self.urlpattern_replace_text])

    def get_emptyvalue_url(self):
        """
        Get the URL to use when the input value is an empty string.

        You should not need to override this.
        """
        return self.build_clear_values_url()

    def get_timeout_milliseconds(self):
        """
        Get the number of milliseconds to wait until applying the change
        when users modify the input field.

        When users hit enter or focus away from the field, search is
        done instantly, so this is only the delay to wait while
        users are typing (live search).
        """
        return 500

    def get_angularjs_options_dict(self):
        options_dict = super().get_angularjs_options_dict()
        options_dict["timeout_milliseconds"] = self.get_timeout_milliseconds()
        options_dict["urlpattern_replace_text"] = self.urlpattern_replace_text
        return options_dict


class IntInputFilterMixin:
    """
    Mixin class that can be used with a subclass of
    :class:`.AbstractInputFilter` to provide int input
    instead of text.

    Must be mixed in **before** :class:`AbstractInputFilter`.
    """

    def get_cleaned_value(self):
        """
        Get the value as an ``int``, or ``None`` (if no value is provided).
        """
        cleaned_value = super().get_cleaned_value()
        if cleaned_value in (None, ""):
            return None
        try:
            return int(cleaned_value)
        except ValueError:
            return None

    def get_placeholder(self):
        return pgettext_lazy("listfilter IntInputFilterMixin", "Type a number ...")


class AbstractSearch(AbstractInputFilter):
    """
    Abstract search filter.

    Subclasses only need to implement
    :meth:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilter.AbstractFilter.filter`.

    See :class:`cradmin_legacy.viewhelpers.listfilter.django.single.textinput.Search`
    for a Django ORM implementation.
    """

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listfilter-filter-single-input-search")
        return css_classes

    def get_placeholder(self):
        return gettext_lazy("Search ...")

    def get_loadingmessage(self):
        return pgettext("listfilter loading message", "Searching")
