from django.core.management.base import NoArgsCommand

from devilry.devilry_elasticsearch_cache import elasticsearch_registry


class Command(NoArgsCommand):
    help = 'Reindex all items in the elasticsearch index.'

    def handle(self, *args, **options):
        elasticsearch_registry.registry.reindex_all()
