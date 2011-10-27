from devilry.simplified import (simplified_modelapi, FieldSpec, FilterSpecs,
                                FilterSpec, PatternFilterSpec)
from devilry.apps.core import models

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedNode(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Node`. """
    class Meta(HasAdminsMixin.MetaMixin):
        """ Defines the CRUD+S methods, the django model to be used, resultfields returned by
        search and which fields can be used to search for a Node object
        using the Simplified API """

        fake_editablefields = ('fake_admins',)
        methods = ['create', 'read', 'update', 'delete', 'search']

        model = models.Node
        resultfields = FieldSpec('id',
                                 'parentnode',
                                 'short_name',
                                 'long_name',
                                 admins=['admins__username'])
        searchfields = FieldSpec('short_name',
                                 'long_name')
        filters = FilterSpecs(FilterSpec('parentnode'),
                              FilterSpec('short_name'),
                              FilterSpec('long_name'),
                              PatternFilterSpec('^(parentnode__)+short_name$'),
                              PatternFilterSpec('^(parentnode__)+long_name$'),
                              PatternFilterSpec('^(parentnode__)+id$'))


    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all node-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return models.Node.where_is_admin_or_superadmin(user)

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given node contains no childnodes or subjects.
        """
        return obj.subjects.all().count() == 0 and obj.child_nodes.all().count() == 0
