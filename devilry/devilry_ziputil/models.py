from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class GenericMeta(models.Model):
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


class CompressedFileMeta(GenericMeta):
    """
    Contains metadata about a compressed archive. Name of the archive, path to it and it's size.
    """

    #: Name of the compressed archive.
    archive_name = models.CharField(max_length=50, null=False, blank=False)

    #: Path to the compressed archive(without archive name).
    archive_path = models.CharField(max_length=200, null=False, blank=False)

    #: Size of the archive in bytes.
    archive_size = models.PositiveIntegerField(null=False)

    def get_full_path(self):
        return '{}/{}'.format(self.archive_path, self.archive_name)

    def __unicode__(self):
        return self.get_full_path()
