# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin.renderable import AbstractRenderableWithCss


class AbstractContainerRenderer(AbstractRenderableWithCss):
    """
    Superclass for all objects table-related elements, such as rows and columnitems.

    This class only defines the inheritance starting point for the elements
    that the tablebuilder consists of.
    """


class AbstractItemRenderer(AbstractContainerRenderer):
    """

    """

    #: If this is specified, we will add an attribute with this name
    #: for the value as an attribute of the object.
    #:
    #: I.e.: if ``valuealias = "person"``, you will be able to use ``me.person`` in
    #: the template, and you will be able to use ``self.person`` in any methods you
    #: add or override in the class (just remember to call ``super()`` if you override
    #: ``__init__``).
    valuealias = None

    def __init__(self, value, **kwargs):
        """
        Args:
            value: The value to render.
        """
        self.value = value
        self.kwargs = kwargs
        if self.valuealias:
            setattr(self, self.valuealias, self.value)


class ColumnHeaderRenderer(AbstractItemRenderer):
    """

    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/builder/base/header_itemvalue.django.html'

    def get_wrapper_htmltag(self):
        return 'th'

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-headeritem']


class ColumnItemRenderer(AbstractItemRenderer):
    """

    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/builder/base/itemvalue.django.html'

    def get_wrapper_htmltag(self):
        return 'td'

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-columnitem']


class ItemFrameRenderer(AbstractContainerRenderer):
    """
    Provides a frame around the item.

    This is typically subclassed to:

    - Add visually highlighted frames for items.
    - Add checkbox for each item.
    - Make the item clickable(via an ``a``-tag or javascript).

    Attributes:
        inneritem: The renderable this frame wraps. An object of :class:`.AbstractContainer` or subclass.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/builder/base/itemframe.django.html'

    def __init__(self, inneritem, **kwargs):
        # super(ItemFrameRenderer, self).__init__(inneritem.value, **kwargs)
        self.inneritem = inneritem

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-itemframe']


class RowRenderer(AbstractContainerRenderer):
    """
    A row that renders its data for each column.

    Attributes:
        renderable_data_list: A list of objects of :class:`.ColumnItemRenderer` or subclass.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/builder/base/row.django.html'

    def __init__(self):
        super(RowRenderer, self).__init__()
        self.renderable_data_list = []

    def iter_renderables(self):
        return iter(self.renderable_data_list)

    def get_wrapper_htmltag(self):
        return 'tr'

    def append(self, renderable):
        self.renderable_data_list.append(renderable)

    def extend(self, renderable_iterable):
        self.renderable_data_list.extend(renderable_iterable)

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-rowitem']


class Table(AbstractRenderableWithCss):
    """
    A table that renders its rows.

    Attributes:
        renderable_rows_list: A list of objects of :class:`.RowRenderer` or subclass objects.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/builder/base/table.django.html'

    def __init__(self, table_headers=None, table_footers=None):
        """
        Args:
            table_headers: Must be a instance of :class:`.RowRenderer` or subclass
                consisting of instances of :class:`.ColumnHeaderRenderer` or subclass.
        """
        self.renderable_rows_theader = []
        self.renderable_rows_list = []
        self.renderable_rows_tfooter = []
        # if table_headers:
        #     self.renderable_rows_list.append(table_headers)
        if table_headers:
            self.renderable_rows_theader.append(table_headers)
        if table_footers:
            self.renderable_rows_tfooter.append(table_footers)

    def iter_renderable_section_header(self):
        """
        Get an iterator over the rows in the table header
        """
        return iter(self.renderable_rows_theader)

    def iter_renderables(self):
        """
        Get an iterator over the rows in the list.
        """
        return iter(self.renderable_rows_list)

    def iter_renderabel_section_footer(self):
        """
        Get an iterator over the rows in the table footer.
        """
        return iter(self.renderable_rows_tfooter)

    def get_wrapper_htmltag(self):
        return 'table'

    def has_items(self):
        """
        Returns:
            bool: ``True`` if the table has any rows, and ``False`` otherwise.

        """
        return len(self.renderable_rows_list) > 0

    def append(self, row_renderer):
        """
        Appends a row to the table.

        Args:
            row_renderer: Must implement the :class:`.RowRenderer` or subclass.
        """
        self.renderable_rows_list.append(row_renderer)

    def extend(self, row_renderer_iterable):
        """
        Same as :meth:`.append` except that is takes an iterable of
        row renderers instead of a single renderable.

        Args:
            row_renderer_iterable: Must be an iterable of objects that implement the :class:`.RowRenderer` or subclass.
        """
        self.renderable_rows_list.extend(row_renderer_iterable)

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-table']
