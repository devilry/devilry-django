import httplib
from django.apps import AppConfig
from django.conf import settings
from django.contrib.sites import requests
from django.db.models.signals import post_save
import elasticsearch
from elasticsearch_dsl.connections import connections
from socket import error as socket_error
from urllib3 import exceptions as urllib3_exceptions

from devilry.devilry_elasticsearch_cache.core_signal_handlers import index_node_post_save


class ElasticsearchCacheAppConfig(AppConfig):
    """
    Connects to the ElasticSearch server using the hosts and
    ports configured in the ``DEVILRY_ELASTICSEARCH_HOSTS`` setting.
    """
    name = 'devilry.devilry_elasticsearch_cache'
    verbose_name = "Devilry elasticsearch cache"

    def ready(self):
        from devilry.apps.core.models import Node
        from devilry.apps.core.models import Period
        from devilry.apps.core.models import Subject
        from devilry.apps.core.models import Assignment

        connections.create_connection(hosts=settings.DEVILRY_ELASTICSEARCH_HOSTS)

        #should be able to run unittests without having the ElasticSearch unittest server
        try:
            httplib.HTTPConnection(settings.DEVILRY_ELASTICSEARCH_HOSTS[0]['host'], settings.DEVILRY_ELASTICSEARCH_HOSTS[0]['port']).connect()
        except socket_error:
            print 'Connection error to ElasticSearch hosts'
            print 'Hint: If you want the model objects to be saved in ES, start the ElasticSearch unittestserver!\nElse ignore this error'
        else:
            post_save.connect(index_node_post_save, sender=Node)
            post_save.connect(index_node_post_save, sender=Subject)
            post_save.connect(index_node_post_save, sender=Period)
            post_save.connect(index_node_post_save, sender=Assignment)