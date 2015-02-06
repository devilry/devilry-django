import logging
from django.db import models
from haystack.signals import BaseSignalProcessor
from haystack.utils import get_identifier

from devilry.devilry_search.tasks import haystack_reindex_object
from devilry.devilry_search.tasks import haystack_delete_object


logger = logging.getLogger(__name__)


class DevilryCelerySignalProcessor(BaseSignalProcessor):

    def reindex_object_on_save(self, sender, instance, **kwargs):
        haystack_reindex_object.delay(get_identifier(instance))

    def reindex_object_on_delete(self, sender, instance, **kwargs):
        haystack_delete_object.delay(get_identifier(instance))

    def setup(self):
        for using in self.connections.connections_info.keys():
            for model_class in self.connections[using].get_unified_index().get_indexed_models():
                logger.info('Detected %r as a Haystack search indexed model.', model_class)
                models.signals.post_save.connect(
                    self.reindex_object_on_save, sender=model_class)
                models.signals.pre_delete.connect(
                    self.reindex_object_on_delete, sender=model_class)

    def teardown(self):
        models.signals.post_save.disconnect(self.reindex_object_on_save)
        models.signals.pre_delete.disconnect(self.reindex_object_on_delete)
