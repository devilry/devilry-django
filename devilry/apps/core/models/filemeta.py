from django.db import models
from django.utils.translation import ugettext as _

from ..deliverystore import load_deliverystore_backend, FileNotFoundError

class FileMeta(models.Model):
    """
    Represents the metadata for a file belonging to a `Delivery`_.

    .. attribute:: delivery

        A django.db.models.OneToOneField_ that points to the `Delivery`_ to
        be given feedback.

    .. attribute:: filename

        Name of the file.

    .. attribute:: size

        Size of the file in bytes.

    .. attribute:: deliverystore

        The current :ref:`DeliveryStore <devilry.apps.core.deliverystore>`.
    """
    delivery = models.ForeignKey("Delivery", related_name='filemetas')
    filename = models.CharField(max_length=255)
    size = models.IntegerField()

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

    def file_exists(self):
        """
        Check if the file exists using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.exists`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.exists(self)

    def read_open(self):
        """
        Open file for reading using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.read_open`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.read_open(self)

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
