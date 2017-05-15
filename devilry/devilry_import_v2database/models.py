from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models


class ImportedModel(models.Model):
    #: Foreignkey to Djangos ContentType.
    content_type = models.ForeignKey(ContentType, related_name='+')

    #: ID of model to store.
    content_object_id = models.PositiveIntegerField(null=False)

    #: An arbitrary model to store.
    content_object = GenericForeignKey('content_type', 'content_object_id')

    #: JSON data from imported v2 models.
    data = JSONField(default={})
