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
    def create_meta(self, instance, archive_path, zipfile_backend):
        """
        Manager provides a way to create a meta entry for a archive.
        See :class:`~devilry.devilry_ziputil.models.CompressedArchiveMeta`.

        Args:
            instance: Instance the archive is for.
            archive_path: Path to achive at storage location.
            zipfile_backend: Backend used to zip the file.
        """
        zipfile_backend.readmode = True
        archive_meta = CompressedArchiveMeta(content_object=instance,
                                             archive_path=archive_path,
                                             archive_location=zipfile_backend.get_storage_location(),
                                             archive_size=zipfile_backend.archive_size())
        archive_meta.clean()
        archive_meta.save()
        return archive_meta


class CompressedArchiveMeta(GenericMeta):
    """
    Contains metadata about a compressed archive. Name of the archive, path to it and it's size.
    """

    objects = CompressedArchiveMetaManager()

    #: When the archive was created.
    created_datetime = models.DateTimeField(auto_now_add=True)

    #: Name of the compressed archive.
    archive_path = models.CharField(max_length=100, null=False, blank=False)

    #: Path to the compressed archive(without archive name).
    archive_location = models.CharField(max_length=200, null=False, blank=False)

    #: Size of the archive in bytes.
    archive_size = models.PositiveIntegerField(null=False, blank=False)

    def get_full_path(self):
        return '{}{}'.format(self.archive_location, self.archive_path)

    def __unicode__(self):
        return self.get_full_path()
