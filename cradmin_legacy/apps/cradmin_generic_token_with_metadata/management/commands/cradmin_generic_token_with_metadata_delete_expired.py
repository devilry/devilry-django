from django.core.management.base import BaseCommand
from cradmin_legacy.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata


class Command(BaseCommand):
    help = "Delete all expired GenericTokenWithMetadata objects from the database."

    def handle(self, **options):
        GenericTokenWithMetadata.objects.delete_expired()
