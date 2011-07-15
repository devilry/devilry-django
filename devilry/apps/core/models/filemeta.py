from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import Q

from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate

from ..deliverystore import load_deliverystore_backend, FileNotFoundError

from datetime import datetime


class FileMeta(models.Model, AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate):
    """
    Represents the metadata for a file belonging to a `Delivery`_.

    .. attribute:: delivery

    A django.db.models.ForeignKey_ that points to the `Delivery`_ of
    the given feedback.

    .. attribute:: filename

        Name of the file.

    .. attribute:: size

        Size of the file in bytes.

    .. attribute:: deliverystore

        The current :ref:`DeliveryStore <devilry.apps.core.deliverystore>`.
    """
    delivery = models.ForeignKey("Delivery", related_name='filemetas')
    filename = models.CharField(max_length=255, help_text=_('Name of the file.'))
    size = models.IntegerField(help_text=_('Size of the file in bytes.'))

    deliverystore = load_deliverystore_backend()

    class Meta:
        app_label = 'core'
        verbose_name = _('FileMeta')
        verbose_name_plural = _('FileMetas')
        unique_together = ('delivery', 'filename')
        ordering = ['filename']

    def remove_file(self):
        """
        Remove the file using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.remove`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.remove(self)

    #TODO delete this?
    #def file_exists(self):
        #"""
        #Check if the file exists using the
        #:meth:`~devilry.core.deliverystore.DeliveryStoreInterface.exists`-method
        #of the :attr:`deliverystore`.
        #"""
        #return self.deliverystore.exists(self)

    #TODO delete this?
    #def read_open(self):
        #"""
        #Open file for reading using the
        #:meth:`~devilry.core.deliverystore.DeliveryStoreInterface.read_open`-method
        #of the :attr:`deliverystore`.
        #"""
        #return self.deliverystore.read_open(self)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(delivery__assignment_group__parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(delivery__assignment_group__parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(delivery__assignment_group__parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(delivery__assignment_group__candidates__identifier=user_obj)

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(delivery__assignment_group__examiners=user_obj)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(delivery__assignment_group__parentnode__admins=user_obj) | \
            Q(delivery__assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(delivery__assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(delivery__assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return self.filename


def filemeta_deleted_handler(sender, **kwargs):
    filemeta = kwargs['instance']
    try:
        filemeta.remove_file()
    except FileNotFoundError, e:
        # TODO: We should have some way of cleaning files which have no
        # corresponding FileMeta from DeliveryStores (could happen if the
        # disk is not mounted when this kicks in..
        pass


from django.db.models.signals import pre_delete, post_save
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
