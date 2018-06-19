from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from devilry.apps.core.models import AssignmentGroup, Candidate, Examiner
from devilry.devilry_comment.models import Comment, CommentFile
from devilry.devilry_group.models import FeedbackSet, GroupComment
from devilry.devilry_merge_v3database.models import TempMergeId
from devilry.devilry_merge_v3database.utils import user_merger, permissiongroup_merger, subject_merger, \
    period_merger, relateduser_merger, assignment_merger, assignment_group_merger, feedbackset_merger, \
    comment_merger
from django.db import transaction


class Command(BaseCommand):
    help = 'Merge Devilry 3 databases.'

    merger_classes = [
        user_merger.UserMerger,
        user_merger.UserNameMerger,
        user_merger.UserEmailMerger,
        permissiongroup_merger.PermissionGroupMerger,
        permissiongroup_merger.PermissionGroupUserMerger,
        subject_merger.SubjectMerger,
        subject_merger.SubjectPermissionGroupMerger,
        period_merger.PeriodMerger,
        period_merger.PeriodPermissionGroupMerger,
        relateduser_merger.RelatedExaminerMerger,
        relateduser_merger.RelatedStudentMerger,
        assignment_merger.AssignmentMerger,
        assignment_group_merger.AssignmentGroupMerger,
        assignment_group_merger.CandidateMerger,
        assignment_group_merger.ExaminerMerger,
        feedbackset_merger.FeedbackSetMerger,
        feedbackset_merger.FeedbackSetPassedPreviousPeriodMerger,
        feedbackset_merger.FeedbackSetGradingUpdateHistoryMerger,
        feedbackset_merger.FeedbackSetDeadlineHistoryMerger,
        comment_merger.CommentMerger,
        comment_merger.GroupCommentMerger,
        comment_merger.CommentFileMerger,
        comment_merger.CommentEditHistoryMerger,
        comment_merger.GroupCommentEditHistoryMerger,
    ]

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

    def __get_migrate_db_model_count_map(self, migrate_from_alias):
        return {
            'assignment_group': AssignmentGroup.objects.using(migrate_from_alias).count(),
            'candidate': Candidate.objects.using(migrate_from_alias).count(),
            'examiner': Examiner.objects.using(migrate_from_alias).count(),
            'feedback_set': FeedbackSet.objects.using(migrate_from_alias).count(),
            'comment': Comment.objects.using(migrate_from_alias).count(),
            'comment_file': CommentFile.objects.using(migrate_from_alias).count(),
            'group_comment': GroupComment.objects.using(migrate_from_alias).count()
        }

    def __get_default_db_model_count_map(self, migrate_from_alias):
        return {
            'assignment_group': AssignmentGroup.objects.count(),
            'candidate': Candidate.objects.count(),
            'examiner': Examiner.objects.count(),
            'feedback_set': FeedbackSet.objects.count(),
            'comment': Comment.objects.count(),
            'comment_file': CommentFile.objects.count(),
            'group_comment': GroupComment.objects.count()
        }

    def __print_result_overview(self, model_verbose_plural, lookup_key, result_map, migrate_map, default_map):
        total_expected_result = migrate_map[lookup_key] + default_map[lookup_key]
        total_result = result_map[lookup_key]
        if total_result == total_expected_result:
            total_result = self.style.SUCCESS(str(total_result))
            total_expected_result = self.style.SUCCESS(str(total_expected_result))
        else:
            total_result = self.style.ERROR(str(total_result))
            total_expected_result = self.style.ERROR(str(total_expected_result))
        self.stdout.write('Number of {}: {} / {}'.format(
            model_verbose_plural,
            total_result,
            total_expected_result))

    def __merge(self, merger_class, migrate_from_alias):
        self.__print_success_message(model=merger_class.model)
        with transaction.atomic():
            merger_class(from_db_alias=migrate_from_alias).run()

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

        # Delete temp merge id entries
        TempMergeId.objects.all().delete()

        # Clear customsql triggers
        call_command('ievvtasks_customsql', clear=True, initialize=False, recreate_data=False)

        # Print number of objects in migrate database
        migrate_db_model_count_map = self.__get_migrate_db_model_count_map(migrate_from_alias=migrate_from_alias)
        self.stdout.write('\n\nMigrate from database num entries of models:')
        self.stdout.write('Number of AssignmentGroups: {}'.format(migrate_db_model_count_map['assignment_group']))
        self.stdout.write('Number of Candidates: {}'.format(migrate_db_model_count_map['candidate']))
        self.stdout.write('Number of Examiners: {}'.format(migrate_db_model_count_map['examiner']))
        self.stdout.write('Number of FeedbackSets: {}'.format(migrate_db_model_count_map['feedback_set']))
        self.stdout.write('Number of Comments: {}'.format(migrate_db_model_count_map['comment']))
        self.stdout.write('Number of CommentFiles: {}'.format(migrate_db_model_count_map['comment_file']))
        self.stdout.write('Number of GroupComments: {}'.format(migrate_db_model_count_map['group_comment']))

        # Print number of objects in default database
        default_db_model_count_map = self.__get_default_db_model_count_map(migrate_from_alias=migrate_from_alias)
        self.stdout.write('\n\nDefault database num entries of models:')
        self.stdout.write('Number of AssignmentGroups: {}'.format(default_db_model_count_map['assignment_group']))
        self.stdout.write('Number of Candidates: {}'.format(default_db_model_count_map['candidate']))
        self.stdout.write('Number of Examiners: {}'.format(default_db_model_count_map['examiner']))
        self.stdout.write('Number of FeedbackSets: {}'.format(default_db_model_count_map['feedback_set']))
        self.stdout.write('Number of Comments: {}'.format(default_db_model_count_map['comment']))
        self.stdout.write('Number of CommentFiles: {}'.format(default_db_model_count_map['comment_file']))
        self.stdout.write('Number of GroupComments: {}'.format(default_db_model_count_map['group_comment']))
        self.stdout.write('\n\n')

        # Start merging
        with transaction.atomic():
            for merger_class in self.merger_classes:
                self.__merge(merger_class=merger_class, migrate_from_alias=migrate_from_alias)

        # Print a count check after database is migrated
        self.stdout.write('\n\nMigrated result:')
        result_db_model_count_map = self.__get_default_db_model_count_map(migrate_from_alias=migrate_from_alias)
        self.__print_result_overview(
            model_verbose_plural='AssignmentGroups',
            lookup_key='assignment_group',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='Candidates',
            lookup_key='candidate',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='Examiners',
            lookup_key='examiner',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='FeedbackSets',
            lookup_key='feedback_set',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='Comments',
            lookup_key='comment',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='CommentFiles',
            lookup_key='comment_file',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)

        self.__print_result_overview(
            model_verbose_plural='GroupComments',
            lookup_key='group_comment',
            result_map=result_db_model_count_map,
            migrate_map=migrate_db_model_count_map,
            default_map=default_db_model_count_map)
        self.stdout.write('\n\n')

        # Initialize customsql triggers and rebuild cache
        call_command('ievvtasks_customsql', initialize=True, recreate_data=True)
