
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from devilry.devilry_qualifiesforexam.models import DraftStatus


class Command(BaseCommand):
    help = "Remove DraftStatus entries from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours-old", dest="hours_old", type=int, default=1, required=False, help="Only delete DraftStatus entries that are older than this many hours."
        )

    def handle(self, *args, **options):
        threshold_datetime = timezone.now() - timezone.timedelta(
            hours=options["hours_old"]
        )
        with transaction.atomic():
            DraftStatus.objects.filter(created_datetime__lt=threshold_datetime).delete()