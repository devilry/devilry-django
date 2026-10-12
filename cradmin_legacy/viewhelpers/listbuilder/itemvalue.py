import json
from xml.sax.saxutils import quoteattr

from cradmin_legacy.viewhelpers.listbuilder import base


class FocusBox(base.ItemValueRenderer):
    """
    Renders a value item as a box styled with the cradmin focus bg as background.

    This is a good default when setting up the structure of views,
    but you will most likely want to create your own
    :class:`cradmin_legacy.viewhelpers.listbuilder.base.ItemValueRenderer`
    subclass for more than the most simple use cases.
    """

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemvalue-focusbox")
        return css_classes


class TitleDescription(FocusBox):
    """
    Extends :class:`.FocusBox` with a template and methods
    that makes it easy to render a view with a title and
    an optional description.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "cradmin_legacy/viewhelpers/listbuilder/itemvalue/titledescription.django.html"

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-listbuilder-itemvalue-titledescription`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemvalue-titledescription")
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
    the ``cradmin-legacy-use-this`` directive.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "cradmin_legacy/viewhelpers/listbuilder/itemvalue/use-this.django.html"

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-listbuilder-itemvalue-usethis`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemvalue-usethis")
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
        context = super().get_context_data(request=request)
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
    template_name = "cradmin_legacy/viewhelpers/listbuilder/itemvalue/edit-delete.django.html"

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-listbuilder-itemvalue-titleeditdelete`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemvalue-editdelete")
        return css_classes

    def get_edit_viewname(self):
        """
        Get the viewname within the current :class:`cradmin_legacy.crapp.App`
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
        Get the viewname within the current :class:`cradmin_legacy.crapp.App`
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
        Get the viewname within the current :class:`cradmin_legacy.crapp.App`
        to go to when viewing. The view is called with ``self.value.id`` as
        argument. If you want to change this behavior, override the
        ``viewbutton-url`` template block.

        This returns ``None`` by default, which means that the button
        is not shown.

        See :class:`.EditDeleteWithPreview`.
        """
        return None


class EditDeleteWithPreviewMixin:
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


class EditDeleteWithArchiveImage(EditDelete):
    """
    Extends :class:`.EditDelete` to include an image from cradmin imagearchive.

    Uses a template that extends the template in :class:`.EditDelete`.
    """

    #: The template used to render this itemvalue.
    #: The template has lots of blocks that you can override.
    template_name = "cradmin_legacy/viewhelpers/listbuilder/itemvalue/edit-delete-with-archive-image.django.html"

    def get_archiveimage(self):
        """
        Get a :class:`cradmin_legacy.apps.cradmin_imagearchive.models.ArchiveImage`
        object to use as the image.
        """
        raise NotImplementedError()

    def get_imagetype(self):
        """
        Get the ``imagetype`` to use to scale/format the image.

        See :func:`cradmin_legacy.templatetags.cradmin_legacy_image_tags.cradmin_create_archiveimage_tag`
        for more information on ``imagetype``.

        Defaults to ``"listbuilder-itemvalue-editdelete"``.
        """
        return "listbuilder-itemvalue-editdelete"

    def get_image_fallbackoptions(self):
        """
        Get the ``fallbackoptions`` to use to scale/format the image.
        These options are used when the imagetype returned by
        :meth:`.get_imagetype` is not defined in the
        :setting:`CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP` setting.

        See :func:`cradmin_legacy.templatetags.cradmin_legacy_image_tags.cradmin_create_archiveimage_tag`
        for more information on ``fallbackoptions``.

        Defaults to::

            {
                'width': 330,
                'height': 400,
                'crop': 'limit',
                'quality': 70,
            }
        """
        return {
            "width": 330,
            "height": 400,
            "crop": "limit",
            "quality": 70,
        }


class EditDeleteWithArchiveImageAndPreview(EditDeleteWithPreviewMixin, EditDeleteWithArchiveImage):
    """
    Shortcut for subclassing :class:`EditDeleteWithPreviewMixin`
    and :class:`.EditDeleteWithArchiveImage`.
    """
