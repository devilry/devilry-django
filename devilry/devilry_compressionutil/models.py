# Django imports
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


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
        unique_together = ('content_type', 'content_object_id')


class CompressedArchiveMetaManager(models.Manager):
    """
    Manager for class :class:`.CompressedArchiveMeta`.
    """
    def create_meta(self, instance, zipfile_backend):
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
                archive_size=zipfile_backend.archive_size()
        )
        archive_meta.clean()
        archive_meta.save()
        return archive_meta


class CompressedArchiveMeta(GenericMeta):
    """
    Metadata about a compressed archive. Name of the archive, path to it and it's size.
    """
    objects = CompressedArchiveMetaManager()

    #: When the archive was created.
    created_datetime = models.DateTimeField(auto_now_add=True)

    #: The actual name of the archive, Example.:``SomeArchive2000.zip``.
    archive_name = models.CharField(max_length=200, blank=False)

    #: Path at storage location of the compressed archive.
    #: Example: ``https://s3-eu-central-1.amazonaws.com/BUCKET/path/to/archive/SomeArchive2000.zip``
    archive_path = models.CharField(max_length=200, blank=False)

    #: Size of the archive in bytes.
    archive_size = models.PositiveIntegerField(null=False, blank=False)

    def __unicode__(self):
        return self.archive_path
