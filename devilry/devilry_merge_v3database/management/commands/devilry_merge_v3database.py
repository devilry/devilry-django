from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from devilry.devilry_merge_v3database.utils import user_merger, permissiongroup_merger, subject_merger, \
    period_merger, relateduser_merger, assignment_merger, assignment_group_merger
from django.db import transaction



class Command(BaseCommand):
    help = 'Merge Devilry 3 databases.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--migrate-from-dbname',
            dest='migrate_from',
            help='The database name to migrate from.')
        parser.add_argument(
            '--clean-reset',
            action='store_true',
            dest='clean_reset',
            default=False,
            help='Resets default database, migrates models and loads a '
                 'test dump into `--migrate-from-dbname`-database!')
        parser.add_argument(
            '--migrate-from-dump-path',
            dest='migrate_from_dump_path',
            help=''
        )

    def __print_success_message(self, model):
        self.stdout.write('Importing {}... {}'.format(
            model.__name__,
            self.style.SUCCESS('OK'))
        )

    def handle(self, *args, **options):
        migrate_from_alias = options.get('migrate_from', None)
        clean_reset = options.get('clean_reset')
        if not migrate_from_alias:
            raise CommandError('--migrate_from_dbname is required')

        if migrate_from_alias not in settings.DATABASES:
            raise CommandError(
                '--migrate_from_dbname "{}" not configured in DATABASES-setting.'.format(migrate_from_alias))

        if clean_reset:
            migrate_from_dump_path = options.get('migrate_from_dump_path', None)
            if not migrate_from_dump_path:
                raise ValueError('migrate-from-dump-path is required if running `--clean-reset`.')
            call_command('dbdev_reinit', database='default')
            call_command('migrate')
            call_command('dbdev_loaddump', migrate_from_dump_path, database='migrate_from')

        # Clear customsql triggers
        call_command('ievvtasks_customsql', clear=True, initialize=False, recreate_data=False)

        with transaction.atomic():
            self.__print_success_message(model=user_merger.UserMerger.model)
            with transaction.atomic():
                user_merger.UserMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=user_merger.UserNameMerger.model)
            with transaction.atomic():
                user_merger.UserNameMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=user_merger.UserEmailMerger.model)
            with transaction.atomic():
                user_merger.UserEmailMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=permissiongroup_merger.PermissionGroupMerger.model)
            with transaction.atomic():
                permissiongroup_merger.PermissionGroupMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=permissiongroup_merger.PermissionGroupUserMerger.model)
            with transaction.atomic():
                permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=subject_merger.SubjectMerger.model)
            with transaction.atomic():
                subject_merger.SubjectMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=subject_merger.SubjectPermissionGroupMerger.model)
            with transaction.atomic():
                subject_merger.SubjectPermissionGroupMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=period_merger.PeriodMerger.model)
            with transaction.atomic():
                period_merger.PeriodMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=period_merger.PeriodPermissionGroupMerger.model)
            with transaction.atomic():
                period_merger.PeriodPermissionGroupMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=relateduser_merger.RelatedExaminerMerger.model)
            with transaction.atomic():
                relateduser_merger.RelatedExaminerMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=relateduser_merger.RelatedStudentMerger.model)
            with transaction.atomic():
                relateduser_merger.RelatedStudentMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=assignment_merger.AssignmentMerger.model)
            with transaction.atomic():
                assignment_merger.AssignmentMerger(from_db_alias=migrate_from_alias).run()

            self.__print_success_message(model=assignment_group_merger.AssignmentGroupMerger.model)
            with transaction.atomic():
                assignment_group_merger.AssignmentGroupMerger(from_db_alias=migrate_from_alias).run()

        # Initialize customsql triggers and rebuild cache
        call_command('ievvtasks_customsql', initialize=True, recreate_data=True)
