# -*- coding: utf-8 -*-


# CrAdmin imports
from cradmin_legacy.renderable import AbstractRenderableWithCss


class AbstractContainerRenderer(AbstractRenderableWithCss):
    """
    Base superclass for all table-related elements, such as rows and columnitems.

    This class only defines the inheritance starting point for the elements
    that the tablebuilder consists of.

    This is mainly used by classes that does not render items directly, but provides an iterator over subclasses of
    :class:`.AbstractContainerRenderer` or :class:`.AbstractItemRenderer`.
    """


class AbstractItemRenderer(AbstractContainerRenderer):
    """
    Superclass for classes that renders an item.

    By item, we mean the actual model, string etc. that should be rendered.
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
            value: The value to render, typically a model or some datatype with information.
        """
        self.value = value
        self.kwargs = kwargs
        if self.valuealias:
            setattr(self, self.valuealias, self.value)


class DataHeaderRenderer(AbstractItemRenderer):
    """
    Class for rendering a header item.

    This adds the opening and closing ``<th>``-tag around the item to be rendered.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/header_itemvalue.django.html'

    def get_wrapper_htmltag(self):
        return 'th'

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-header']


class DataItemRenderer(AbstractItemRenderer):
    """

    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/itemvalue.django.html'

    def get_wrapper_htmltag(self):
        return 'td'

    def get_base_css_classes_list(self):
        return ['devilry-tablebuilder-data']


class RowRenderer(AbstractContainerRenderer):
    """
    A row that renders its data for each column.

    Attributes:
        renderable_data_list: A list of objects of :class:`.ColumnItemRenderer` or subclass.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/row.django.html'

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
        return ['devilry-tablebuilder-row']


class Table(AbstractRenderableWithCss):
    """
    A table that renders its rows.

    Attributes:
        renderable_rows_list: A list of objects of :class:`.RowRenderer` or subclass objects.
    """
    template_name = 'devilry_cradmin/devilry_tablebuilder/table.django.html'

    def __init__(self, table_headers=None, table_footers=None):
        """
        Args:
            table_headers: Must be a instance of :class:`.RowRenderer` or subclass
                consisting of instances of :class:`.ColumnHeaderRenderer` or subclass.
        """
        self.renderable_rows_theader = []
        self.renderable_rows_list = []
        self.renderable_rows_tfooter = []
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
