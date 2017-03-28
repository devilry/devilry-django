# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import renderable
from django_cradmin.viewhelpers.listbuilder import base


class AbstractCellRenderer(renderable.AbstractRenderableWithCss):
    """
    Abstract class for cells which cell-renderers should inherit from.
    """
    template_name = 'devilry_cradmin/new_devilry_tablebuilder/base_cell.django.html'

    def get_base_css_classes_list(self):
        return ['devilry-tabulardata-list__cell']


class AbstractRowList(base.List):
    """
    Abstract class that inherits for ``base.List``.

    The subclasses that inherits from this has access to ``renderable_list`` where renderables can be added.
    """
    template_name = 'devilry_cradmin/new_devilry_tablebuilder/base_row.django.html'


class AbstractListAsTable(base.List):
    """
    Abstract class for a list used as a table.

    Subclass this and override ``__init__`` to add the desired data to be used in the table.
    """
    template_name = 'devilry_cradmin/new_devilry_tablebuilder/base_tablebuilder.django.html'

    def __init__(self, is_paginated=False, page_obj=None):
        """
        Args:
            is_paginated: Used if pagination is desired. Support must be added to template.
            page_obj: Used if pagination is desired. Support must be added to template.
        """
        super(AbstractListAsTable, self).__init__()
        self.header_renderable_list = []
        self.is_paginated = is_paginated
        self.page_obj = page_obj

        self.add_header()
        self.add_rows()

    def iter_header_renderables(self):
        """
        Returns:
            (iterator): iterator over the renderables in the header list.
        """
        return iter(self.header_renderable_list)

    def append_header_renderable(self, renderable):
        """
        Appends an item to the header list.

        The header is a distinct part of the list, and is rendered first.

        Args:
            renderable: Must implement the :class:`django_cradmin.renderable.AbstractRenderableWithCss` interface.
        """
        self.header_renderable_list.append(renderable)

    def add_header(self):
        """
        Override this and add renderables to the "table header" with ``self.append_header_renderable(renderable)``.
        """
        raise NotImplementedError()

    def add_rows(self):
        """
        Override this and add renderables to the "table body" with ``self.append(renderable)``.
        """
        raise NotImplementedError()

    def get_context_data(self, request=None):
        context_data = super(AbstractListAsTable, self).get_context_data(request=request)
        context_data['is_paginated'] = self.is_paginated
        context_data['page_obj'] = self.page_obj
        return context_data
