import logging
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete

from .abstract_is_admin import AbstractIsAdmin
from .abstract_is_examiner import AbstractIsExaminer
from .abstract_is_candidate import AbstractIsCandidate
from ..deliverystore import load_deliverystore_backend

log = logging.getLogger(__name__)


class FileMeta(models.Model, AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate):
    """
    Represents the metadata for a file belonging to a `Delivery`_.

    A file meta is just information about a single file, which is stored in a
    :attr:`deliverystore`. Use the :attr:`deliverystore` to manage the file
    stored in its physical location. Example::

        filemeta = FileMeta.objects.get(pk=0)
        if filemeta.deliverystore.exists(filemeta):
            filemeta.deliverystore.remove(filemeta)

        # Write or read just as with the builtin open()
        fobj = filemeta.deliverystore.write_open(filemeta)
        fobj.write('Hello')
        fobj.write('World')
        fobj.close()
        fobj = filemeta.deliverystore.read_open(filemeta)
        print fobj.read()

    See :ref:`DeliveryStore <devilry.apps.core.deliverystore>` for more details on deliverystores.

    .. attribute:: delivery

    A django.db.models.ForeignKey_ that points to the `Delivery`_ of
    the given feedback.

    .. attribute:: filename

        Name of the file.

    .. attribute:: size

        Size of the file in bytes.

    .. attribute:: deliverystore

        The current :ref:`DeliveryStore <devilry.apps.core.deliverystore>`.
        *Class variable*.
    """
    MAX_FILENAME_LENGTH = 255

    delivery = models.ForeignKey("core.Delivery", related_name='filemetas', on_delete=models.CASCADE)
    filename = models.CharField(max_length=MAX_FILENAME_LENGTH, help_text='Name of the file.')
    size = models.IntegerField(help_text='Size of the file in bytes.')

    deliverystore = load_deliverystore_backend()

    class Meta:
        app_label = 'core'
        verbose_name = 'FileMeta'
        verbose_name_plural = 'FileMetas'
        unique_together = ('delivery', 'filename')
        ordering = ['filename']

    @classmethod
    def q_published(cls, old=True, active=True):
        now = timezone.now()
        q = Q(delivery__deadline__assignment_group__parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(delivery__deadline__assignment_group__candidates__identifier=user_obj)

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(delivery__deadline__assignment_group__examiners__user=user_obj)

    def __str__(self):
        return self.filename

    def get_all_data_as_string(self):
        """
        Get all data store in the deliverystore for this FileMeta as a string.
        THIS IS ONLY FOR TESTING, and should NEVER be used for production code,
        since it will eat all memory on the server for huge files.
        """
        fileobj = self.deliverystore.read_open(self)
        data = fileobj.read()
        fileobj.close()
        return data

    def copy(self, newdelivery):
        """
        Copy this filemeta into ``newdelivery``. Copies the database object and
        the data in the deliverystore.
        """
        copy = FileMeta(delivery=newdelivery,
                        filename=self.filename,
                        size=self.size)
        copy.full_clean()
        copy.save()
        self.deliverystore.copy(self, copy)


def filemeta_deleted_handler(sender, **kwargs):
    filemeta = kwargs['instance']
    filemeta.deliverystore.remove(filemeta)


pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
