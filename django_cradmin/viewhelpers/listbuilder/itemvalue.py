import json
from builtins import str
from xml.sax.saxutils import quoteattr

from django_cradmin.viewhelpers.listbuilder import base


class FocusBox(base.ItemValueRenderer):
    """
    Renders a value item as a box styled with the cradmin focus bg as background.

    This is a good default when setting up the structure of views,
    but you will most likely want to create your own
    :class:`django_cradmin.viewhelpers.listbuilder.base.ItemValueRenderer`
    subclass for more than the most simple use cases.
    """

    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(FocusBox, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-focus-box")
        return css_class_suffixes

    def get_base_css_classes_list(self):
        css_classes = super(FocusBox, self).get_base_css_classes_list()
        css_classes.append("django-cradmin-listbuilder-itemvalue-focusbox")
        return css_classes


class TitleDescription(FocusBox):
    """
    Extends :class:`.FocusBox` with a template and methods
    that makes it easy to render a view with a title and
    an optional description.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "django_cradmin/viewhelpers/listbuilder/itemvalue/titledescription.django.html"

    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(FocusBox, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-title-description")
        return css_class_suffixes

    def get_base_css_classes_list(self):
        """
        Adds the ``django-cradmin-listbuilder-itemvalue-titledescription`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super(TitleDescription, self).get_base_css_classes_list()
        css_classes.append("django-cradmin-listbuilder-itemvalue-titledescription")
        return css_classes

    def get_title(self):
        """
        Get the title of the box.

        Defaults to ``str(self.value)``.
        """
        return str(self.value)

    def get_description(self):
        """
        Get the description (shown below the title).

        Defaults to ``None``, which means that no description
        is rendered.
        """
        return None


class UseThis(TitleDescription):
    """
    Renders a value item with a *Use this* button that uses
    the ``django-cradmin-use-this`` directive.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "django_cradmin/viewhelpers/listbuilder/itemvalue/use-this.django.html"

    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(FocusBox, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-use-this")
        return css_class_suffixes

    def get_base_css_classes_list(self):
        """
        Adds the ``django-cradmin-listbuilder-itemvalue-usethis`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super(UseThis, self).get_base_css_classes_list()
        css_classes.append("django-cradmin-listbuilder-itemvalue-usethis")
        return css_classes

    def get_use_this_directive_options_dict(self, request):
        return {
            "value": self.value.pk,
            "fieldid": request.GET["foreignkey_select_fieldid"],
            "preview": self.get_title(),
        }

    def get_use_this_directive_options_json(self, request):
        return quoteattr(json.dumps(self.get_use_this_directive_options_dict(request=request)))

    def get_context_data(self, request=None):
        context = super(UseThis, self).get_context_data(request=request)
        context["use_this_directive_options_json"] = self.get_use_this_directive_options_json(request=request)
        return context


class EditDelete(TitleDescription):
    """
    Extends :class:`.TitleDescription` with a template that makes it very easy
    to render a box that provides edit and delete buttons.

    The renderer also allows you to specify a description,
    and the template has lots of blocks that makes it easy to insert
    more content or override the existing content.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "django_cradmin/viewhelpers/listbuilder/itemvalue/edit-delete.django.html"

    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(FocusBox, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-edit-delete")
        return css_class_suffixes

    def get_base_css_classes_list(self):
        """
        Adds the ``django-cradmin-listbuilder-itemvalue-titleeditdelete`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super(EditDelete, self).get_base_css_classes_list()
        css_classes.append("django-cradmin-listbuilder-itemvalue-editdelete")
        return css_classes

    def get_edit_viewname(self):
        """
        Get the viewname within the current :class:`django_cradmin.crapp.App`
        to go to when editing. The view is called with ``self.value.id`` as
        argument. If you want to change this behavior, override the
        ``editbutton-url`` template block.

        This returns ``"edit"`` by default, and we recommend that you
        name the view for editing items this to keep things uniformly
        structured.
        """
        return "edit"

    def get_delete_viewname(self):
        """
        Get the viewname within the current :class:`django_cradmin.crapp.App`
        to go to when deleting. The view is called with ``self.value.id`` as
        argument. If you want to change this behavior, override the
        ``deletebutton-url`` template block.

        This returns ``"delete"`` by default, and we recommend that you
        name the view for deleting items this to keep things uniformly
        structured.
        """
        return "delete"

    def get_preview_viewname(self):
        """
        Get the viewname within the current :class:`django_cradmin.crapp.App`
        to go to when viewing. The view is called with ``self.value.id`` as
        argument. If you want to change this behavior, override the
        ``viewbutton-url`` template block.

        This returns ``None`` by default, which means that the button
        is not shown.

        See :class:`.EditDeleteWithPreview`.
        """
        return None


class EditDeleteWithPreviewMixin(object):
    """
    Mixin class for :class:`.EditDelete` that adds a view button that
    shows a preview via the view named ``"preview"`` in the current app
    (the viewname can be overridden in
    :meth:`.EditDeleteWithPreviewMixin.get_preview_viewname`).

    Examples:

        Add a view button to :class:`.EditDelete`::

            class EditDeleteWithPreview(EditDeleteWithPreviewMixin, EditDelete):
                pass

        .. note::

            The example above is the same as using :class:`.EditDeleteWithPreviewMixin`.
    """

    def get_preview_viewname(self):
        """
        Overrides :meth:`.EditDelete.get_preview_viewname` to make it return
        ``"preview"`` by default instead of ``None``.
        """
        return "preview"


class EditDeleteWithPreview(EditDeleteWithPreviewMixin, EditDelete):
    """
    Shortcut for subclassing :class:`EditDeleteWithPreviewMixin`
    and :class:`.EditDelete`.
    """

    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(EditDeleteWithPreview, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-edit-delete-with-preview")
        return css_class_suffixes
