from django.core.management.base import BaseCommand

from devilry.devilry_compressionutil.models import CompressedArchiveMeta


class Command(BaseCommand):
    help = 'Create new user.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            dest='days',
            help='Archives older than X number of days will be deleted. X must be higher than 0.')
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Delete all compressed archives.'
        )

    def handle(self, *args, **options):
        delete_all = options.get('all')
        days = options.get('days')
        if delete_all:
            CompressedArchiveMeta.objects.all().delete()
        if days:
            if days < 1:
                self.stdout.write('--days must be higher than 0.')
            CompressedArchiveMeta.objects.delete_compressed_archive(older_than_days=int(days))
