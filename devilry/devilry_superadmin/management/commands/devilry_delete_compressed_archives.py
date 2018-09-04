from django.core.management.base import BaseCommand

from devilry.devilry_compressionutil.models import CompressedArchiveMeta


class Command(BaseCommand):
    help = 'Delete compressed archives.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            dest='days',
            type=int,
            help='Archives older than X number of days will be deleted. X must be higher than 0.')
        parser.add_argument(
            '--seconds',
            dest='seconds',
            type=int,
            help='Archives older than X seconds will be deleted. X must be higher than 0.')
        parser.add_argument(
            '--deleted',
            action='store_true',
            default=False,
            help='Delete all compressed archives marked as deleted.')
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Delete all compressed archives.')

    def handle(self, *args, **options):
        delete_all = options.get('all')
        delete_marked_as_deleted = options.get('deleted')
        num_days = options.get('days')
        num_seconds = options.get('seconds')

        if (delete_all and num_days) \
            or (delete_all and num_seconds) \
            or (num_days and num_seconds):
            self.stdout.write('You can only provide one of the following parameters, --all, --days, and --seconds')

        if delete_all:
            CompressedArchiveMeta.objects.all().delete()

        if num_days:
            if num_days < 1:
                self.stdout.write('--days must be higher than 0.')
            CompressedArchiveMeta.objects.delete_compressed_archives_older_than(days=num_days)

        if num_seconds:
            if num_seconds < 1:
                self.stdout.write('--seconds must be higher than 0.')
            CompressedArchiveMeta.objects.delete_compressed_archives_older_than(seconds=num_seconds)

        if delete_marked_as_deleted:
            CompressedArchiveMeta.objects.delete_compressed_archives_marked_as_deleted()
