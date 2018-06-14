from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from devilry.devilry_merge_v3database.utils import user_merger, permissiongroup_merger, subject_merger
from django.db import transaction


class Command(BaseCommand):
    help = 'Merge Devilry 3 databases.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--migrate_from_dbname',
            dest='migrate_from',
            help='The database name to migrate from.')

    def handle(self, *args, **options):
        migrate_from_alias = options.get('migrate_from', None)

        if not migrate_from_alias:
            raise CommandError('--migrate_from_dbname is required')

        if migrate_from_alias not in settings.DATABASES:
            raise CommandError(
                '--migrate_from_dbname "{}" not configured in DATABASES-setting.'.format(migrate_from_alias))

        with transaction.atomic():
            user_merger.UserMerger(from_db_alias=migrate_from_alias).run()
            user_merger.UserNameMerger(from_db_alias=migrate_from_alias).run()
            user_merger.UserEmailMerger(from_db_alias=migrate_from_alias).run()
            permissiongroup_merger.PermissionGroupMerger(from_db_alias=migrate_from_alias).run()
            permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=migrate_from_alias).run()
            subject_merger.SubjectMerger(from_db_alias=migrate_from_alias).run()

