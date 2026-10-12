from builtins import str as textstr
from collections import OrderedDict
import json
import re
import logging
import warnings
from xml.sax.saxutils import quoteattr

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template import defaultfilters
from django.template.defaultfilters import truncatechars
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.db import models
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers.listfilter import listfilter_viewmixin

logger = logging.getLogger(__name__)


class Column:
    #: The model field rendered in this column. It is not required,
    #: but if you do not, you have to override :meth:`.get_header`
    #: and :meth:`.render_value`.
    modelfield = None

    #: A field to use for ordering of this model. Can also be a join, like ``company__name``.
    #: If this is not specified, :obj:`.modelfield` is used. If none of them are used,
    #: or if you want to sort using multiple fields, you must override :meth:`.get_orderby_args`
    #: and :meth:`.is_sortable`.
    orderingfield = None

    #: The template used to render a cell in the Column.
    template_name = None

    #: The column width. See :meth:`.get_column_width`.
    column_width = None

    #: The name of the template context object.
    #: The object is always available as ``object``, but you
    #: can override this to make it available by another name.
    context_object_name = None

    #: The name of the template context variable containing the return value from
    #: meth:`.get_value`.
    #: This is always available as ``value``, but you
    #: can override this to make it available by another name.
    context_value_name = None

    #: List of css classes to add to the header cell in this column.
    #: See :meth:`.get_headercell_css_classes`.
    headercell_css_classes = []

    #: List of css classes to add to all the non-header cells in this column.
    #: See :meth:`.get_normalcells_css_classes`.
    normalcells_css_classes = []

    #: List of css classes to add to both normal cells and the header cell in this column.
    #: See :meth:`.get_allcells_css_classes`.
    allcells_css_classes = []

    def __init__(self, view, columnindex):
        self.view = view
        self.columnindex = columnindex

    def get_header(self):
        """
        Get the header of the column. Defaults to the ``verbose_name``
        of the :obj:`.modelfield`.
        """
        if self.modelfield:
            field = self.view.model._meta.get_field(self.modelfield)
            return field.verbose_name
        else:
            raise NotImplementedError()

    def get_column_width(self):
        """
        Returns the column width. Setting this is generally not recommended, but
        sometimes you need exact scaling of the column.

        Example legal values: ``"100px", "20%"``. Defaults to :obj:`.column_width`.
        """
        return self.column_width

    def get_headercell_css_style(self):
        """
        Get the css styles of the header cell of the column.
        Defaults to setting :meth:`.get_column_width` as a css style.

        You normally want to avoid setting styles with this and use
        :meth:`.get_headercell_css_class_string` instead, but this is provided for
        those cases where setting the style attribute is the only decent solution.
        """
        column_width = self.get_column_width()
        if column_width:
            return f"width: {column_width}"
        else:
            return ""

    def get_headercell_css_classes(self):
        """
        Get the css classes of the header cell in this column.

        Returns:
            A list of css classes. Defaults to :obj:`.headercell_css_classes`.
        """
        return self.headercell_css_classes

    def get_headercell_css_class_string(self):
        """
        Get the css class of the header cell of the column.
        Defaults to setting the ``objecttableview-sortable-header``
        class if :meth:`.is_sortable`.
        """
        css_classes = self.get_headercell_css_classes() + self.get_allcells_css_classes()
        if self.is_sortable():
            css_classes.append("objecttableview-sortable-header")
        return " ".join(css_classes)

    def get_normalcells_css_classes(self):
        """
        Get the css classes of all the normal (non-header) cells in this
        column.

        Returns:
            A list of css classes. Defaults to :obj:`.normalcells_css_classes`.
        """
        return self.normalcells_css_classes

    def get_normalcell_css_class_string(self):
        """
        Get the css class of the header cell of the column.
        You normally do not override this. Override
        :meth:`.get_normalcells_css_classes` instead.
        """
        css_classes = self.get_normalcells_css_classes() + self.get_allcells_css_classes()
        return " ".join(css_classes)

    def get_normalcell_css_style(self):
        """
        Get the css styles of the header cell of the column.
        Defaults to setting :meth:`.get_column_width` as a css style.

        You normally want to avoid setting styles with this and use
        :meth:`.get_normalcell_css_class_string` instead, but this is provided for
        those cases where setting the style attribute is the only decent solution.
        """
        column_width = self.get_column_width()
        if column_width:
            return f"width: {column_width}"
        else:
            return ""

    def get_allcells_css_classes(self):
        """
        Get css classes that should be added to all cells in this
        column, including the header cell.

        Returns:
            A list of css classes. Defaults to :obj:`.allcells_css_classes`.
        """
        return self.allcells_css_classes

    def reverse_appurl(self, name, args=[], kwargs={}):
        return self.view.request.cradmin_app.reverse_appurl(name, args=args, kwargs=kwargs)

    def render_value(self, obj):
        if self.modelfield:
            return getattr(obj, self.modelfield)
        else:
            raise NotImplementedError()

    def get_context_data(self, obj):
        """
        Get context data for rendering the cell (see :meth:`.render_cell_content`.
        """
        value = self.render_value(obj)
        context = {"value": value, "object": obj}
        if self.context_object_name:
            context[self.context_object_name] = obj
        if self.context_value_name:
            context[self.context_value_name] = value
        return context

    def get_template_name(self, obj):
        """
        Returns the template name to use for the given ``obj``.
        Defaults to :obj:`~.Column.template_name`.
        """
        return self.template_name

    def render_cell_content(self, obj):
        """
        Render the cell using the template specifed in :obj:`.template_name`.
        """
        context_data = self.get_context_data(obj)
        return render_to_string(self.get_template_name(obj), context_data, request=self.view.request)

    def get_flip_ordering_url(self):
        """
        Used in the template to get the URL when a user clicks on the header.
        Should not be overridden.
        """
        return self.view._get_flip_ordering_url_for_column(self.columnindex)

    def get_remove_ordering_url(self):
        """
        Used in the template to get the URL when a user clicks on the remove ordering button in the header.
        Should not be overridden.
        """
        return self.view._get_remove_ordering_url_for_column(self.columnindex)

    @property
    def orderinginfo(self):
        if not hasattr(self, "_orderinginfo"):
            if self.is_sortable():
                self._orderinginfo = self.view._get_orderinginfo_for_column(self.columnindex)
            else:
                self._orderinginfo = None
        return self._orderinginfo

    def is_ordered(self):
        return self.orderinginfo and self.orderinginfo.order_ascending is not None

    def is_sortable(self):
        """
        Specifies if this column is sortable.

        Defaults to ``True`` if :obj:`.modelfield` or :obj:`.orderingfield`
        is defined.
        """
        return bool(self.modelfield) or bool(self.orderingfield)

    def get_orderby_args(self, order_ascending):
        """
        Get the a list of ``QuerySet.order_by`` arguments that should be applied
        when the user requests the given ``sortorder`` for this column.

        If you set :obj:`.orderingfield`, the value is generated from that. If
        :obj:`.orderingfield` is not defined, we fall back on :obj:`.modelfield`.

        Parameters:
            order_ascending (bool): ``True`` if we should return the orderby arguments
                for ascending ordering, and ``False`` for descending ordering.
        """
        sortprefix = ""
        if not order_ascending:
            sortprefix = "-"
        orderingfield = self.orderingfield or self.modelfield
        if orderingfield:
            return [f"{sortprefix}{orderingfield}"]
        else:
            raise NotImplementedError("You must override get_orderby_args, set orderingfield or set modelfield.")

    def get_default_order_is_ascending(self):
        """
        Determine if the default ordering for the field shown in this column is
        ascending.

        .. deprecated:: 1.0.0-beta.019

            Replaced by :meth:`.get_default_ordering`.

        Returns:
            ``True`` if the default ordering is ascending.
            ``False`` if the default ordering is descending.
            ``None`` if no default ordering is configured for this column.
        """
        raise NotImplementedError("get_default_order_is_ascending() has been replaced by get_default_ordering().")

    def get_default_ordering(self):
        """
        Get default ordering for this column.

        Tries to determine a sane default using the following algorithm:

        1. Check if :obj:`~.Column.orderingfield` is defined. If it is,
           check if it is part of ``model._meta.ordering``, and set default
           ordering accordingly. If it is not in ``model._meta.ordering``,
           return ``None`` (no default ordering).
        2. Same as (1), but using :obj:`~.Column.modelfield`.
        3. Raise NotImplementedError - rarely happens since most column types
           eighter have overridden this method (if sorting makes not sense),
           or have at least :obj:`~.Column.modelfield` defined.

        Returns:
            A string describing the default ordering of this column:

            - ``"asc"``: If the default ordering is ascending.
            - ``"desc"``: If the default ordering is descending.
            - ``None``: If we should not apply default ordering.
        """
        orderingfield = self.orderingfield or self.modelfield
        if orderingfield:
            default_ordering = self.view.model._meta.ordering
            descending_orderingfield = f"-{orderingfield}"
            if orderingfield in default_ordering:
                return "asc"
            elif descending_orderingfield in default_ordering:
                return "desc"
            else:
                return None
        else:
            raise NotImplementedError(
                "You must return False from is_sortable(), override "
                "get_default_ordering(), set orderingfield or set modelfield."
            )

    def get_and_validate_default_ordering(self):
        """
        Used internally by the framework. Should not be overridden.
        """
        try:
            default_ordering = self.get_default_ordering()
            if default_ordering in ("asc", "desc", None):
                return default_ordering
            else:
                raise ValueError('get_default_ordering() must return one of: "asc", "desc", None.')
        except NotImplementedError:
            # Temporary fallback for the deprecated get_default_order_is_ascending() method.
            warnings.warn(
                "get_default_order_is_ascending() has been replaced by get_default_ordering().", DeprecationWarning
            )
            order_ascending = self.get_default_order_is_ascending()
            if order_ascending is None:
                return None
            elif order_ascending is True:
                return "asc"
            else:
                return "desc"


class PlainTextColumn(Column):
    template_name = "cradmin_legacy/viewhelpers/objecttable/plaintextcolumn-cell.django.html"


class DatetimeColumn(PlainTextColumn):
    datetime_format = "SHORT_DATETIME_FORMAT"

    def render_value(self, obj):
        value = super().render_value(obj)
        if value is None:
            return None
        else:
            return defaultfilters.date(value, self.datetime_format)


class TruncatecharsPlainTextColumn(PlainTextColumn):
    """
    A variant of :class:`.PlainTextColumn` that truncates the text down to
    a configurable length. The length is configured in :obj:`.maxlength`.
    """

    #: Maximum length of the value displayed in the column.
    maxlength = 30

    def render_value(self, obj):
        value = super().render_value(obj)
        if value is None:
            return None
        else:
            return truncatechars(value, self.maxlength)


class SingleActionColumn(Column):
    """
    A column where the entire content is a link.

    Usage::

        class MySingleActionColumn(SingleActionColumn):
            def get_actionurl(self, obj):
                return reverse('something')

    See also: :class:`.MultiActionColumn`.
    """

    template_name = "cradmin_legacy/viewhelpers/objecttable/singleactioncolumn-cell.django.html"

    def get_actionurl(self, obj):
        raise NotImplementedError()

    def get_context_data(self, obj):
        context = super().get_context_data(obj=obj)
        context["action_url"] = self.get_actionurl(obj)
        return context


class SingleButtonColumn(Column):
    """
    A column where the entire content is a single :class:`.AbstractButton`.

    Usage::

        class MySingleActionColumn(SingleActionColumn):
            def get_actionurl(self, obj):
                return reverse('something')

    See also: :class:`.MultiActionColumn`.
    """

    template_name = "cradmin_legacy/viewhelpers/objecttable/singlebuttoncolumn-cell.django.html"

    def render_value(self, obj):
        return None

    def get_button(self, obj):
        raise NotImplementedError()

    def get_context_data(self, obj):
        context = super().get_context_data(obj=obj)
        context["button"] = self.get_button(obj).render()
        return context


class ImagePreviewColumn(Column):
    template_name = "cradmin_legacy/viewhelpers/objecttable/imagepreviewcolumn-cell.django.html"

    #: See :meth:`.ImagePreviewColumn.get_preview_imagetype`.
    preview_imagetype = None

    def is_sortable(self):
        return False

    def get_preview_imagetype(self):
        """
        Get the ``imagetype`` to use with
        :func:`~cradmin_legacy.templatetags.cradmin_legacy_image_tags.cradmin_create_archiveimage_tag`.
        to generate the preview.
        """
        return self.preview_imagetype

    def get_context_data(self, obj):
        context = super().get_context_data(obj=obj)
        imagefieldfile = self.render_value(obj)
        imageurl = None
        if imagefieldfile:
            imageurl = imagefieldfile.url
        context.update(
            {
                "imageurl": imageurl,
                "preview_imagetype": self.get_preview_imagetype(),
                "preview_fallbackoptions": {"width": 100, "height": 60},
            }
        )
        return context


class MultiActionColumn(Column):
    template_name = "cradmin_legacy/viewhelpers/objecttable/multiactioncolumn-cell.django.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_buttons(self, obj):
        """
        Get an iterable over the buttons/actions for the given ``obj``.

        Returns:
            An iterable yielding :class:`.Button` objects.
        """
        raise NotImplementedError()

    def get_context_data(self, obj):
        context = super().get_context_data(obj=obj)
        context["buttons"] = self.get_buttons(obj)
        return context


class UseThisActionColumn(Column):
    template_name = "cradmin_legacy/viewhelpers/objecttable/usethisactioncolumn-cell.django.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_buttons(self, obj):
        """
        Get an iterable over the buttons/actions for the given ``obj``.

        Returns:
            An iterable yielding :class:`.Button` objects.
        """
        raise NotImplementedError()

    def get_context_data(self, obj):
        context = super().get_context_data(obj=obj)
        context["buttons"] = self.get_buttons(obj)
        return context


class AbstractButton:
    """
    Abstract base class for buttons.
    """

    #: The django template name/path.
    template_name = "cradmin_legacy/viewhelpers/objecttable/button.django.html"

    #: The HTML element to use for the button.
    button_element = "a"

    def __init__(self, label, buttonclass="btn btn-default btn-sm", icon=None, dom_id=None):
        """
        Parameters:
            label (unicode): The label of the button.
            url (unicode): The url/href attribute of the button.
            icon (unicode): An icon to show alongside the label. Example: ``fa fa-thumbs-up``.
            buttonclass (unicode): The css class to use for the button. Defaults to ``btn btn-default btn-sm``.
            dom_id (unicode): If this is not None, it sets the id-attribute of the dom node for the button element.
        """
        self.label = label
        self.icon = icon
        self.buttonclass = buttonclass
        self.dom_id = dom_id

    def get_attributes(self):
        """
        Deprectated - use :meth:`.get_data_attributes`.
        """
        return self.get_data_attributes()

    def get_data_attributes(self):
        """
        Returns a dict of custom data attributes to add to the button.
        They are automatically escaped and prefixed with ``data-``
        before they are added to the button.

        Override this, call super, and extend the dict to add your
        own template context data.
        """
        return {}

    def get_html_attributes(self):
        """
        Returns a dict of custom HTML attributes to add to the button.
        They are automatically escaped before they are added to the button.

        Override this, call super, and extend the dict to add your
        own template context data.
        """
        attributes = {}
        if self.buttonclass:
            attributes["class"] = self.buttonclass
        if self.dom_id:
            attributes["id"] = self.dom_id
        return attributes

    def __iter_attributes(self):
        for attrname, value in list(self.get_html_attributes().items()):
            attrvalue = quoteattr(value)
            yield f"{attrname}={attrvalue}"
        for key, value in list(self.get_data_attributes().items()):
            attrname = f"data-{key}"
            attrvalue = quoteattr(value)
            yield f"{attrname}={attrvalue}"

    def get_context_data(self):
        """
        Get the template context data. Must be overridden in subclasses.

        Override this, call super, and extend the dict to add your
        own template context data.
        """
        return {
            "label": self.label,
            "icon": self.icon,
            "buttonclass": self.buttonclass,
            "dom_id": self.dom_id,
            "attributes": self.__iter_attributes(),
            "button_element": self.button_element,
        }

    def render(self):
        return render_to_string(self.template_name, self.get_context_data())


class Button(AbstractButton):
    """
    A pythonic interface for creating a HTML link styled as a button.

    Used by:

    - :meth:`.ObjectTableView.get_buttons`.
    - :meth:`.MultiActionColumn.get_buttons`
    """

    def __init__(self, url="#", **kwargs):
        """
        Parameters:
            url (unicode): The url/href attribute of the button.
            kwargs: See :class:`.AbstractButton`.
        """
        self.url = url
        super().__init__(**kwargs)

    def get_html_attributes(self):
        attributes = super().get_html_attributes()
        attributes.update(
            {
                "href": self.url,
            }
        )
        return attributes


class NonSubmitButton(AbstractButton):
    """
    A pythonic interface for creating a HTML ``<button type="button">``
    """

    button_type = "button"
    button_element = "button"

    def __init__(self, value=None, name=None, **kwargs):
        self.value = value
        self.name = name
        super().__init__(**kwargs)

    def get_html_attributes(self):
        attributes = super().get_html_attributes()
        attributes.update(
            {
                "type": self.button_type,
            }
        )
        if self.value is not None:
            attributes["value"] = self.value
        if self.name is not None:
            attributes["name"] = self.name
        return attributes


class SubmitButton(NonSubmitButton):
    """
    A pythonic interface for creating a HTML ``<button type="submit">``
    """

    button_type = "submit"


class PagePreviewsButton(AbstractButton):
    """
    A button variant that uses the ``cradmin-legacy-page-preview-open-on-click``
    AngularJS directive to open previews in an overlay containing an IFRAME.

    Unlike :class:`.PagePreviewButton`, this supports multiple previews
    in a single IFRAME. Users can switch between the previews using
    a navigation bar.

    For this to work, you need to set :obj:`.ObjectTableView.enable_previews` to ``True``
    (or override :meth:`.ObjectTableView.get_enable_previews`).
    """

    button_element = "button"

    def __init__(self, urls, **kwargs):
        """
        Parameters:
            urls (list): A list of dicts.
                Each dict configures a preview url with the following keys::

                    {
                        "label": "<THE LABEL IN THE NAVBAR HERE>",
                        "url": "<THE URL HERE>",
                        "open_label": "<LABEL FOR OPEN IN NEW WINDOW HERE>",
                        "css_classes": "<OPTIONAL KEY WHERE YOU CAN SPECIFY A CSS CLASS>"
                    }

                The first item url will be shown by default, but the user
                will be able to switch to the other urls by clicking in a
                navigation list.
            kwargs: See :class:`.AbstractButton`.
        """
        self.urls = urls
        super().__init__(**kwargs)

    def get_data_attributes(self):
        attributes = super().get_data_attributes()
        attributes.update({"cradmin-legacy-page-preview-open-on-click": json.dumps({"urls": self.urls})})
        return attributes


class PagePreviewButton(PagePreviewsButton):
    """
    A button variant that uses the ``cradmin-legacy-page-preview-open-on-click``
    AngularJS directive to open a preview in an overlay containing an IFRAME.
    Works just like a regular button. The only difference is that the url is
    opened in the IFRAME in the overlay instead of in the current window.

    For this to work, you need to set :obj:`.ObjectTableView.enable_previews` to ``True``
    (or override :meth:`.ObjectTableView.get_enable_previews`).
    """

    def __init__(self, url, **kwargs):
        urls = [
            {
                "label": "Unused",  # Never shown because the navbar is hidden when we only have one URL.
                "url": url,
            }
        ]
        super().__init__(urls=urls, **kwargs)


class UseThisButton(Button):
    """
    Button for :class:`.UseThisActionColumn`.
    """

    def __init__(self, view, label, obj, buttonclass="btn btn-default btn-sm"):
        self.view = view
        self.obj = obj
        super().__init__(label=label, buttonclass=buttonclass)

    def get_data_attributes(self):
        attributes = {
            "cradmin-legacy-use-this": json.dumps(
                {
                    "value": self.obj.pk,
                    "fieldid": self.view.request.GET["foreignkey_select_fieldid"],
                    "preview": self.view.make_foreignkey_preview_for(self.obj),
                }
            )
        }
        return attributes


class ForeignKeySelectButton(Button):
    """
    Used to make buttons that lead to views that handle foreign key selection.

    It is just like a normal :class:`.Button`, except that it requires a request
    object, and uses that to set success_url to the current URL.
    """

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.url = "{}?{}".format(
            self.url, urlencode({"foreignkey_select_mode": "1", "success_url": request.get_full_path()})
        )


class MultiSelectAction:
    """
    Used to define multiselect actions for
    :meth:`.ObjectTableView.get_multiselect_actions`.
    """

    def __init__(self, label, url):
        self.label = label
        self.url = url

    def serialize(self):
        return {"label": textstr(self.label), "url": self.url}


class ColumnOrderingInfo:
    @classmethod
    def from_orderingstringentry(cls, orderingstringindex, orderingstringentry):
        order_ascending = orderingstringentry.startswith("a")
        columnindex = int(orderingstringentry[1:])
        return cls(orderingstringindex=orderingstringindex, columnindex=columnindex, order_ascending=order_ascending)

    @classmethod
    def create_orderingstringentry(cls, columnindex, order_ascending):
        if order_ascending:
            prefix = "a"
        else:
            prefix = "d"
        return f"{prefix}{columnindex}"

    def __init__(self, orderingstringindex, columnindex, order_ascending):
        self.orderingstringindex = orderingstringindex
        self.columnindex = columnindex
        self.order_ascending = order_ascending

    def to_orderingstringentry(self):
        return self.__class__.create_orderingstringentry(self.columnindex, self.order_ascending)

    def __str__(self):
        return f"{self.orderingstringindex}:{self.to_orderingstringentry()}"


class OrderingStringParser:
    """
    Parses an ordering string (the ordering querystring argument for objecttable).

    Parameters:
        orderingstring (str):
            A ``.``-separated list of the character ``a`` or ``d`` followed by
            a 0-based column index. The character described the order we want
            to sort the column at the given index (a: ascending, d: descending).

            The order of the entries in the comma separated list has significance.
            For the sortstring ``a3,a1,a2``, we will sort by column 3 first,
            then by column 1 and then by column 2 (all ascending).

            Note that the OrderingStringParser only describes what columns to
            order and in what direction, not by what fields each column is ordered.
    """

    def __init__(self, orderingstring):
        self.orderingstring = orderingstring
        self.orderingdict = OrderedDict()
        if self.orderingstring:
            if re.match(r"^([ad]\d+\.)*([ad]\d+)$", self.orderingstring):
                for orderingstringindex, orderingstringentry in enumerate(self.orderingstring.split(".")):
                    orderinginfo = ColumnOrderingInfo.from_orderingstringentry(
                        orderingstringindex=orderingstringindex, orderingstringentry=orderingstringentry
                    )
                    self.orderingdict[orderinginfo.columnindex] = orderinginfo
            else:
                logger.debug("Invalid value for ordering: %r", self.orderingstring)

    def remove_column(self, columnindex):
        """
        Return an orderingstring on the same format as the one parsed by this class
        with the given ``columnindex`` removed.
        """
        out = []
        for index, orderinginfo in list(self.orderingdict.items()):
            if index != columnindex:
                out.append(orderinginfo.to_orderingstringentry())
        return ".".join(out)

    def flip_column(self, columnindex):
        """
        Return an orderingstring on the same format as the one parsed by this class
        with the ordering direction of the given ``columnindex`` flipped/reversed.

        If the given column is not ordered, we add it last with ascending ordering.
        """
        out = []
        found = False
        for index, orderinginfo in list(self.orderingdict.items()):
            if index == columnindex:
                found = True
                order_ascending = not orderinginfo.order_ascending
                out.append(
                    ColumnOrderingInfo.create_orderingstringentry(
                        columnindex=columnindex, order_ascending=order_ascending
                    )
                )
            else:
                out.append(orderinginfo.to_orderingstringentry())
        if not found:
            out.append(ColumnOrderingInfo.create_orderingstringentry(columnindex=columnindex, order_ascending=True))
        return ".".join(out)

    def get(self, columnindex):
        return self.orderingdict.get(columnindex, None)

    def __len__(self):
        return len(self.orderingdict)


class SearchForm(forms.Form):
    search = forms.CharField(required=True)


class ObjectTableView(ListView):
    """
    A view inspired by the changelist in ``django.contrib.admin``.

    Lets say you use company as the role in your admin site, and
    you want each company to have a repository of documents that
    they can offer for download. To make a list of all uploaded
    documents, you would do something like this::

        from cradmin_legacy.viewhelpers.objecttable import ObjectTableView
        from myapp.models import Document

        class DocumentListView(ObjectTableView):
            model = Document

            def get_queryset_for_role(self, company):
                return self.model.objects.filter(
                    company=company)

    """

    #: Paginate by this number of items. You can safely override this.
    paginate_by = 30

    #: The template used to render the view. You can override this,
    #: but if you override it, you should extend the default template
    #: (cradmin_legacy/viewhelpers/objecttable/objecttable.django.html).
    template_name = "cradmin_legacy/viewhelpers/objecttable/objecttable.django.html"

    #: The template used to render the no items message.
    #: See :meth:`.get_no_items_message_template_name` and
    #: :meth:`.get_no_items_message`
    no_items_message_template_name = "cradmin_legacy/viewhelpers/objecttable/no-items-message.django.html"

    #: The template used to render the no searchresults message.
    #: See :meth:`.get_no_searchresults_message_template_name` and
    #: :meth:`.get_no_searchresults_message`
    no_searchresults_message_template_name = (
        "cradmin_legacy/viewhelpers/objecttable/no-searchresults-message.django.html"
    )

    #: Set this to ``True`` to make the template not render the menu.
    #: Very useful when creating foreign-key select views, and other views
    #: where you do not want your users to accidentally click out of the
    #: current view.
    hide_menu = False

    #: The model class to list objects for. You do not have to specify
    #: this, but if you do not specify this or :meth:`~.ObjectTableView.get_model_class`,
    #: you have to override :meth:`~.ObjectTableView.get_pagetitle` and
    #: :meth:`~.ObjectTableView.get_no_items_message`.
    model = None

    #: Defines the columns in the table. See :meth:`.get_columns`.
    columns = []

    #: The fields to search.
    #: Setting this enables search. If you implement a custom
    #: :meth:`.filter_search` method that does not make use of
    #: ``searchfields``, you can override :meth:`.enable_search`
    #: instead of setting this to some fake value.
    searchfields = []

    #: The default implementation of :meth:`.filter_search` uses this comparator
    #: when searching the given :obj:`.searchfields`.
    search_comparator = "icontains"

    #: The search placeholder text. See :meth:`.get_search_placeholder_text`. Defaults to "Search...".
    search_placeholder_text = gettext_lazy("Search...")

    #: Enable previews? See :meth:`.get_enable_previews`. Defaults to ``False``.
    enable_previews = False

    #: Hide column headers? Setting this to ``True`` adds the ``sr-only`` class
    #: to the thead-element, which makes the columns hide, but still available for
    #: accessibility purposes.
    hide_column_headers = False

    #: Set this to True to hide the page header. See :meth:`.FormViewMixin.get_hide_page_header`.
    hide_page_header = False

    def get_model_class(self):
        """
        Get the model class to list objects for.

        Defaults to :obj:`~.ObjectTableView.model`. See :obj:`~.ObjectTableView.model` for more info.
        """
        return self.model

    def get_hide_page_header(self):
        """
        Return ``True`` if we should hide the page header.

        You can override this, or set :obj:`.hide_page_header`, or hide the page header
        in all listing views with the ``CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_LISTINGVIEWS`` setting.
        """
        return self.hide_page_header or getattr(settings, "CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_LISTINGVIEWS", False)

    def get_no_items_message_template_name(self):
        """
        Return the template name to use for the no items message.

        Defaults to :obj:`~.ObjectTableView.no_items_message_template_name`.
        """
        return self.no_items_message_template_name

    def get_no_items_message_context_data(self):
        """
        Get the context data for :meth:`.get_no_items_message_template_name`.
        """
        return {
            "modelname_plural": self.get_model_class()._meta.verbose_name_plural.lower(),
            "request": self.request,
        }

    def get_no_items_message(self):
        """
        Get the message to show when there are no items.

        Renders the :meth:`.get_no_items_message_template_name` template with
        :meth:`.get_no_items_message_context_data` as context data.
        """
        return render_to_string(self.get_no_items_message_template_name(), self.get_no_items_message_context_data())

    def get_no_searchresults_message_template_name(self):
        """
        Return the template name to use for the no searchresults message.

        Defaults to :obj:`~.ObjectTableView.no_searchresults_message_template_name`.
        """
        return self.no_searchresults_message_template_name

    def get_no_searchresults_message_context_data(self):
        """
        Get the context data for :meth:`.get_no_searchresults_message_template_name`.
        """
        return {
            "request": self.request,
        }

    def get_no_searchresults_message(self):
        """
        Get the message to show when there are no searchresults.

        Renders the :meth:`.get_no_searchresults_message_template_name` template with
        :meth:`.get_no_searchresults_message_context_data` as context data.
        """
        return render_to_string(
            self.get_no_searchresults_message_template_name(), self.get_no_searchresults_message_context_data()
        )

    def get_search_placeholder_text(self):
        """
        Returns the search placeholder text. Defaults to :obj:`.search_placeholder_text`.

        Only used if search is enabled (see :obj:`.searchfields`).
        """
        return self.search_placeholder_text

    def get_enable_previews(self):
        """
        If this returns ``True``, we enable previews. When previews are
        enabled, you can add :class:`.PagePreviewButton` to columns
        to show previews.

        Defaults to :obj:`.enable_previews`.
        """
        return self.enable_previews

    def get_multiselect_actions(self):
        """
        Multiselect actions. If this returns a non-empty iterator, each row
        has a cell with a select box in the first column. Selecting at least
        one of the rows will reveal a dropdown menu with all the available
        actions.

        Returns:
            An iterator (list, tuple, ...) yielding :class:`.MultiSelectAction`
            objects. Returns an empty list by default.
        """
        return []

    def get_columns(self):
        """
        Get the columns in the table. Defaults to :obj:`.columns`.

        A list where each entry can be the name of any field on the
        :class:`model`, or a subclass of :class:`.Column`.
        """
        return self.columns

    def get_buttons(self):
        """
        Override this to add some buttons/global actions for this table.

        Examples:

            Simple example::

                def get_buttons(self):
                    app = self.request.cradmin_app
                    return [
                        objecttable.Button('Create', url=app.reverse_appurl('create')),
                        objecttable.Button('Delete all', url=app.reverse_appurl('deleteall')),
                    ]
        """
        return []

    def get_queryset_for_role(self, role):
        """
        Get a queryset with all objects of :obj:`~.ObjectTableView.model`  that
        the current role can access.
        """
        raise NotImplementedError()

    def enable_search(self):
        """
        Enable search?

        The default implementation returns ``True`` if :obj:`.searchfields` is
        not empty.
        """
        return len(self.searchfields) > 0 and self.queryset_contains_items()

    def get_queryset(self):
        """
        DO NOT override this. Override :meth:`.get_queryset_for_role`
        instead.
        """
        self.current_search_matchcount = None
        queryset = self.get_queryset_for_role(self.request.cradmin_role)
        orderby = []
        for columnobject, orderinginfo in self.__iter_columnobjects_with_orderinginfo():
            orderby.extend(columnobject.get_orderby_args(orderinginfo.order_ascending))
        if orderby:
            queryset = queryset.order_by(*orderby)
        if self.enable_search():
            searchform = SearchForm(self.request.GET)
            self.current_search = ""
            if searchform.is_valid():
                self.current_search = searchform.cleaned_data["search"]
                queryset = self.filter_search(searchstring=self.current_search, queryset=queryset)
                self.current_search_matchcount = queryset.count()
        return queryset

    def _get_columnobjects(self):
        """
        Build the :obj:`.columns` list into a list of :class:`Column` objects.
        """
        if not hasattr(self, "__columns"):
            self.__columns = []
            for columnindex, columnclass in enumerate(self.get_columns()):
                if isinstance(columnclass, textstr):
                    columnclass = type("SimpleColumn", (PlainTextColumn,), dict(modelfield=columnclass))
                self.__columns.append(columnclass(view=self, columnindex=columnindex))
        return self.__columns

    def get_row_css_classes_for_object(self, obj):
        """
        Get CSS classes for the row rendering the given ``obj``.

        Returns:
            An empty list by default, but you can override this
            and return css classes as a list. Typical examples
            are:

            - Styling of rows disabled objects.
            - Styling of extra important objects.

            The css classes is applied to the ``<tr>`` element.
        """
        return []

    def __get_row_css_classes_string_for_object(self, obj):
        return " ".join(self.get_row_css_classes_for_object(obj))

    def __create_row(self, obj):
        return {
            "object": obj,
            "css_classes": self.__get_row_css_classes_string_for_object(obj),
            "cells": [(column, column.render_cell_content(obj)) for column in self._get_columnobjects()],
        }

    def __iter_table(self, object_list):
        for obj in object_list:
            yield self.__create_row(obj)

    def queryset_contains_items(self):
        if not hasattr(self, "_queryset_contains_items"):
            self._queryset_contains_items = self.get_queryset_for_role(self.request.cradmin_role).exists()
        return self._queryset_contains_items

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to the ``verbose_name_plural`` of the :obj:`~.ObjectTableView.model`
        with the first letter capitalized.
        """
        return defaultfilters.capfirst(self.get_model_class()._meta.verbose_name_plural)

    def get_pageheading(self):
        """
        Get the page heading.

        Defaults to :meth:`.get_pagetitle`.
        """
        return self.get_pagetitle()

    def _get_search_hidden_fields(self):
        for key, value in list(self.request.GET.items()):
            if key not in ("search", "page"):
                yield key, value

    def _get_pager_extra_querystring(self):
        querystring_dict = self.request.GET.copy()

        if "page" in querystring_dict:
            del querystring_dict["page"]

        if querystring_dict:
            querystring = {}
            for k, v in querystring_dict.items():
                querystring[k] = v
            return urlencode(querystring)
        else:
            return ""

    def make_foreignkey_preview_for(self, obj):
        return textstr(obj)

    def _get_use_this_hidden_attribute(self):
        pk = self.request.GET["foreignkey_selected_value"]
        obj = get_object_or_404(self.get_queryset_for_role(self.request.cradmin_role), pk=pk)
        data = json.dumps(
            {
                "value": obj.pk,
                "fieldid": self.request.GET["foreignkey_select_fieldid"],
                "preview": self.make_foreignkey_preview_for(obj),
            }
        )
        return quoteattr(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = context["object_list"]

        multiselect_actions = self.get_multiselect_actions()
        form_action = self.get_form_action()
        if form_action and multiselect_actions:
            raise ValueError(
                "You can not configure both a form action "
                "(get_form_action) and enable multiselect "
                "(via get_multiselect_actions) at the same time."
            )
        if multiselect_actions:
            context["multiselect_actions"] = json.dumps([action.serialize() for action in multiselect_actions])
        if form_action:
            context["form_action"] = form_action

        context["pagetitle"] = self.get_pagetitle()
        context["pageheading"] = self.get_pageheading()
        context["columns"] = self._get_columnobjects()
        context["table"] = list(self.__iter_table(object_list))
        context["buttons"] = self.get_buttons()
        context["enable_search"] = self.enable_search()
        context["enable_previews"] = self.get_enable_previews()
        context["cradmin_hide_menu"] = self.hide_menu
        context["hide_column_headers"] = self.hide_column_headers
        if self.enable_search():
            context["current_search"] = self.current_search
            context["search_hidden_fields"] = self._get_search_hidden_fields()
            context["focus_on_searchfield"] = self.focus_on_searchfield()
            context["current_search_matchcount"] = self.current_search_matchcount
            context["no_searchresults_message"] = self.get_no_searchresults_message()
        context["pager_extra_querystring"] = self._get_pager_extra_querystring()
        context["multicolumn_ordering"] = len(self.__parse_orderingstring()) > 1
        context["queryset_contains_items"] = self.queryset_contains_items()
        context["no_items_message"] = self.get_no_items_message()
        context["hide_pageheader"] = self.get_hide_page_header()

        # Handle foreignkey selection
        if "foreignkey_selected_value" in self.request.GET:
            context["use_this_hidden_attribute"] = self._get_use_this_hidden_attribute()

        return context

    def __create_orderingstring_from_default_ordering(self):
        orderinglist = []
        for columnindex, columnobject in enumerate(self._get_columnobjects()):
            if columnobject.is_sortable():
                default_ordering = columnobject.get_and_validate_default_ordering()
                if default_ordering:
                    orderinglist.append(
                        ColumnOrderingInfo.create_orderingstringentry(
                            columnindex=columnindex, order_ascending=default_ordering == "asc"
                        )
                    )
        return ".".join(orderinglist)

    def __parse_orderingstring(self):
        if not hasattr(self, "__orderingstringparser"):
            orderingstring = self.request.GET.get("ordering", None)
            if orderingstring is None:
                orderingstring = self.__create_orderingstring_from_default_ordering()
            self.__orderingstringparser = OrderingStringParser(orderingstring)
        return self.__orderingstringparser

    def _url_with_querystringarg_changed(self, querystringarg, newvalue):
        querystring = self.request.GET.copy()
        querystring[querystringarg] = newvalue
        return f"{self.request.path}?{querystring.urlencode()}"

    def _get_flip_ordering_url_for_column(self, columnindex):
        return self._url_with_querystringarg_changed(
            querystringarg="ordering", newvalue=self.__parse_orderingstring().flip_column(columnindex)
        )

    def _get_remove_ordering_url_for_column(self, columnindex):
        return self._url_with_querystringarg_changed(
            querystringarg="ordering", newvalue=self.__parse_orderingstring().remove_column(columnindex)
        )

    def _get_orderinginfo_for_column(self, columnindex):
        return self.__parse_orderingstring().get(columnindex)

    def __iter_columnobjects_with_orderinginfo(self):
        columnobjects = self._get_columnobjects()
        for orderinginfo in list(self.__parse_orderingstring().orderingdict.values()):
            try:
                columnobject = columnobjects[orderinginfo.columnindex]
            except IndexError:
                pass
            else:
                yield (columnobject, orderinginfo)

    def filter_search(self, queryset, searchstring):
        """
        Filter the queryset on search.

        The default implementation uses :obj:`.search_comparator` to compare
        earch of the :obj:`.searchfields` with the given ``searchstring``.
        This does not give a very good search experience, but it works
        fine for small data sets.

        If you want to use a search engine, you should make sure your
        search engine can yield a list of ids/primary-keys, and override
        this method with something like this::

             def filter_search(self, queryset, searchstring):
                ids = my_searchengine.search(searchstring)
                return queryset.filter(id__in=ids)

        If you use a custom search engine, you will most likely also want
        to override :meth:`.enable_search` and just return ``True``.
        """
        if self.searchfields:
            query = None
            for fieldname in self.searchfields:
                kwargs = {f"{fieldname}__{self.search_comparator}": searchstring}
                fieldquery = models.Q(**kwargs)
                if query:
                    query |= fieldquery
                else:
                    query = fieldquery
            queryset = queryset.filter(query).distinct()
        return queryset

    def get_form_action(self):
        """
        Get the ``action`` attribute of the form wrapping the entire
        listing.

        You will typically use this if you have buttons with a value attribute
        within your form and you want to submit that value to a view.

        You can not use this if you enable multiselect
        (see :meth:`.get_multiselect_actions`).
        """
        return None

    def focus_on_searchfield(self):
        """
        If this returns ``True`` (the default), the view will set focus to the
        search field on load (I.E.: Place the cursor in the search field).

        No used if search is not enabled.
        """
        return True


class FilterListMixin(listfilter_viewmixin.ViewMixin):
    """
    Mixin for adding filtering with :doc:`viewhelpers.listfilter <viewhelpers_listfilter>` to
    :class:`.ObjectTableView`.

    Must be mixed in before :class:`.ObjectTableView`.
    """

    def get_filterlist_position(self):
        """
        Get the position where you want to place the filterlist.

        Supported values are:

        - left
        - right (the default)
        - top

        Defaults to ``"top"`` if :meth:`.get_filterlist_class` returns
        :class:`cradmin_legacy.viewhelpers.listfilter.lists.Horizontal` or a subclass of it,
        otherwise ``"right"``.
        """
        filterlist_class = self.get_filterlist_class()
        if issubclass(filterlist_class, listfilter.lists.Horizontal):
            return "top"
        else:
            return "right"

    def get_filterlist_template_name(self):
        """
        Get the template to use based on what :meth:`.get_filterlist_position`.

        You will want to call this from the ``get_template_names`` method.
        This is just the interface, refer to the mixins implemented in
        various modules (such as :class:`cradmin_legacy.viewhelpers.listbuilderview.FilterListMixin`)
        for details on how to use this method.
        """
        position = self.get_filterlist_position()
        template_name = f"cradmin_legacy/viewhelpers/objecttable/objecttable-filterlist-{position}.django.html"
        return template_name

    def get_filter_unprotected_querystring_arguments(self):
        """
        This returns ``{'page'}``, which ensures we go back to
        page 1 when changing a filter.

        See :class:`cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin`
        for more details.
        """
        return {"page"}

    def get_filterlist_target_dom_id(self):
        """
        Overrides
        :meth:`cradmin_legacy.viewhelpers.listfilter.listfilter_viewmixin.ViewMixin.get_filterlist_target_dom_id`
        with a default of ``"cradmin_legacy_objecttableview_tablewrapper"``.

        You should not need to override this unless you create a completely custom
        template for your view.
        """
        return "cradmin_legacy_objecttableview_tablewrapper"
