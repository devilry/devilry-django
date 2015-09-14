from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import models

from basenode import BaseNode
from custom_db_fields import ShortNameField, LongNameField
from devilry.devilry_account.models import User
from model_utils import Etag


class Node(models.Model, BaseNode, Etag):
    """
    This class is typically used to represent a hierarchy of institutions,
    faculties and departments.


    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node, which
        is always a `Node`_.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.

    .. attribute:: child_nodes

        A set of child_nodes of type `Node`_ for this node

    .. attribute:: subjects

        A set of :class:`subjects <devilry.apps.core.models.Subject>` for this node

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    """
    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey('self', blank=True, null=True,
                                   related_name='child_nodes')
    admins = models.ManyToManyField(User, blank=True)
    etag = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    def _can_save_id_none(self, user_obj):
        if self.parentnode is not None and self.parentnode.is_admin(user_obj):
            return True
        else:
            return False

    def get_path(self):
        if self.parentnode:
            return self.parentnode.get_path() + "." + self.short_name
        else:
            return self.short_name

    def iter_childnodes(self):
        """
        Recursively iterates over all child nodes, and their child nodes.
        For a list of direct child nodes, use atribute child_nodes instead.
        """
        for node in Node.objects.filter(parentnode=self):
            yield node
            for c in node.iter_childnodes():
                yield c

    def clean(self):
        """Validate the node, making sure it does not do something stupid.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - The node is it's own parent.
            - The node is the child of itself or one of its childnodes.
        """
        if self.parentnode == self:
            raise ValidationError(_('A node can not be it\'s own parent.'))

        if not self.short_name:
            raise ValidationError(_('Short Name is a required attribute.'))

        greater_than_count = 1
        if self.id is None:
            greater_than_count = 0

        if self.parentnode:
            if Node.objects.filter(short_name=self.short_name). \
                    filter(parentnode__pk=self.parentnode.id).count() > greater_than_count:
                raise ValidationError(_('A node can not have the same '
                                        'short name as another within the same parent.'))
        else:
            if Node.objects.filter(short_name=self.short_name). \
                    filter(parentnode=None).count() > greater_than_count:
                raise ValidationError(_('A root node can not have the same '
                                        'short name as another root node.'))
        for node in self.iter_childnodes():
            if node == self.parentnode:
                raise ValidationError(_('A node can not be the child of one of it\'s own children.'))
        super(Node, self).clean()

    @classmethod
    def _get_nodepks_where_isadmin(cls, user_obj):
        """
        Get a list with the primary key of all nodes where the given
        `user_obj` is admin.

        WARNING:
        This method is not private! It is used by many models in core,
        and in ``devilry_nodeadmin.rest.aggregatedstudentinfo``.
        """
        admnodes = Node.objects.filter(admins=user_obj)
        l = []

        def add_admnodes(admnodes):
            for a in admnodes.all():
                l.append(a.pk)
                add_admnodes(a.child_nodes)

        add_admnodes(admnodes)
        return l

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(pk__in=cls._get_nodepks_where_isadmin(user_obj))

    def is_empty(self):
        """
        Returns ``True`` if this Node does not contain any childnodes or subjects.
        """
        return self.child_nodes.count() == 0 and self.subjects.count() == 0
