# Django imports
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy, pgettext_lazy

from devilry.devilry_compressionutil import backend_registry


class GenericMeta(models.Model):
    """
    Abstract class that implements usage of GenericForeignKey.
    """
    #: Foreignkey to Djangos ContentType.
    content_type = models.ForeignKey(ContentType, related_name='content_type_compressed_file_meta')

    #: ID of model to store.
    content_object_id = models.PositiveIntegerField(null=False)

    #: An arbitrary model to store.
    content_object = GenericForeignKey('content_type', 'content_object_id')

    class Meta:
        abstract = True

        #: Can only exist one meta model for each model it references
        #: with its GenericForeignKey.
        # unique_together = ('content_type', 'content_object_id')


class CompressedArchiveMetaQueryset(models.QuerySet):
    """
    Manager for class :class:`.CompressedArchiveMeta`.
    """
    def create_meta(self, instance, zipfile_backend, user, user_role=''):
        """
        Manager provides a way to create a meta entry for a archive.
        See :class:`~devilry.devilry_ziputil.models.CompressedArchiveMeta`.

        Args:
            instance: Instance the archive is for.
            zipfile_backend: base backend for compression,
                see :class:`~devilry_ziputil.backends.backend_base.PythonZipFileBackend`.
        """
        zipfile_backend.readmode = True
        archive_meta = CompressedArchiveMeta(
                content_object=instance,
                archive_name=zipfile_backend.archive_name,
                archive_path=zipfile_backend.archive_path,
                archive_size=zipfile_backend.archive_size(),
                backend_id=zipfile_backend.backend_id,
                created_by=user,
                created_by_role=user_role
        )
        archive_meta.clean()
        archive_meta.save()
        return archive_meta

    def __delete_compressed_archive(self, **timedelta_kwargs):
        """
        Expects timedelta kwars (days, seconds, microseconds, etc..)
        """
        older_than_datetime = timezone.now() - timezone.timedelta(**timedelta_kwargs)
        self.filter(created_datetime__lte=older_than_datetime).delete()

    def delete_compressed_archives_older_than(self, days=None, seconds=None):
        """
        Delete compressed archive meta entries older than a specified number of days or seconds.

        Args:
            older_than_days (int): Delete everything older than this.
            older_than_seconds (int): Delete everything older than this.
        """
        if days:
            self.__delete_compressed_archive(days=days)
        elif seconds:
            self.__delete_compressed_archive(seconds=seconds)

    def delete_compressed_archives_marked_as_deleted(self):
        """
        Delete all compressed archives marked as deleted.
        """
        self.filter(deleted_datetime__isnull=False).delete()


class CompressedArchiveMeta(GenericMeta):
    """
    Metadata about a compressed archive. Name of the archive, path to it and it's size.
    """
    objects = CompressedArchiveMetaQueryset.as_manager()

    #: Who created the archive.
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True, default=None,
        on_delete=models.SET_NULL
    )

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as a student.
    CREATED_BY_ROLE_STUDENT = 'student'

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as an examiner.
    CREATED_BY_ROLE_EXAMINER = 'examiner'

    #: Use this as value for :obj:`~.Comment.user_role` if the user
    #: is commenting as an admin.
    CREATED_BY_ROLE_ADMIN = 'admin'

    #: Choices for the :obj:`~.Comment.user_role` field.
    CREATED_BY_ROLE_CHOICES = (
        (CREATED_BY_ROLE_STUDENT, pgettext_lazy('compressed archive meta role', 'Student')),
        (CREATED_BY_ROLE_EXAMINER, pgettext_lazy('compressed archive meta role', 'Examiner')),
        (CREATED_BY_ROLE_ADMIN, pgettext_lazy('compressed archive meta role', 'Admin')),
    )

    #: What role did the user create the archive with?
    created_by_role = models.CharField(
        choices=CREATED_BY_ROLE_CHOICES,
        max_length=255,
        default=''
    )

    #: When the archive was created.
    created_datetime = models.DateTimeField(auto_now_add=True)

    #: The actual name of the archive, Example.:``SomeArchive2000.zip``.
    archive_name = models.CharField(max_length=200, blank=False)

    #: Path at storage location of the compressed archive.
    #: Example: ``https://s3-eu-central-1.amazonaws.com/BUCKET/path/to/archive/SomeArchive2000.zip``
    archive_path = models.CharField(max_length=200, blank=False)

    #: Size of the archive in bytes.
    archive_size = models.PositiveIntegerField(null=False, blank=False)

    #: The ID of the backend used.
    #: This is the ID attribute
    #: :attr:`~.devilry.devilry_compressionutil.backends.backends_base.BaseArchiveBackend.backend_id`.
    backend_id = models.CharField(max_length=100, blank=True, null=False, default='')

    #: When the entry was marked for deletion.
    deleted_datetime = models.DateTimeField(null=True, default=None)

    def clean(self):
        if backend_registry.Registry.get_instance().get(self.backend_id) is None:
            raise ValidationError({
                'backend_id': ugettext_lazy('backend_id must refer to a valid backend')
            })

    def __unicode__(self):
        return self.archive_path


@receiver(pre_delete, sender=CompressedArchiveMeta)
def pre_compressed_archive_meta_delete(sender, instance, **kwargs):
    compressed_archive_meta = instance
    backend_class = backend_registry.Registry.get_instance().get(compressed_archive_meta.backend_id)
    backend_class.delete_archive(full_path=compressed_archive_meta.archive_path)

