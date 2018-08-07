import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from devilry.devilry_import_v2database import modelimporters


class TimeExecution(object):
    def __init__(self, label, command):
        self.start_time = None
        self.label = label
        self.command = command

    def __enter__(self):
        self.start_time = timezone.now()

    def __exit__(self, ttype, value, traceback):
        end_time = timezone.now()
        duration_minutes = (end_time - self.start_time).total_seconds() / 60.0
        self.command.stdout.write('{}: {}min'.format(self.label, duration_minutes))
        self.command.stdout.write('')


class Command(BaseCommand):
    args = '<input-directory>'
    help = 'Import the entire Devilry v2 database from a directory of json files.'

    def add_arguments(self, parser):
        parser.add_argument(
            'input-directory',
            help='The input directory - a directory created with '
                 '"devilry_dump_database_for_v3_migration" with Devilry 2.x.')
        parser.add_argument(
            '--start-at',
            dest='start_at_importer_classname',
            choices=self.__get_all_importer_classnames(),
            help='Name of the importer to start at. Skips any importers before this '
                 'importer.')
        parser.add_argument(
            '--stop-at',
            dest='stop_at_importer_classname',
            choices=self.__get_all_importer_classnames(),
            help='Name of the importer to stop at. Skips any importers after this '
                 'importer.')
        parser.add_argument(
            '--fake',
            dest='fake', action='store_true',
            default=False,
            help='Print a summary of the import, but do not import anything.')

    def __abort_if_input_directory_does_not_exist(self):
        if self.fake:
            return

        if not os.path.exists(self.input_directory):
            self.stderr.write('The input directory, {}, does not exist. Aborting.'.format(
                self.input_directory
            ))
            raise SystemExit()

    def handle(self, *args, **options):
        self.input_directory = options['input-directory']
        self.fake = options['fake']
        self.start_at_importer_classname = options['start_at_importer_classname']
        self.stop_at_importer_classname = options['stop_at_importer_classname']
        v2_media_root = getattr(settings, 'DEVILRY_V2_MEDIA_ROOT', None)
        if not v2_media_root:
            self.stderr.write('WARNING: settings.DEVILRY_V2_MEDIA_ROOT is not set,'
                              'so StaticFeedback attachments will not be imported.')
        v2_delivery_file_root = getattr(settings, 'DEVILRY_V2_DELIVERY_FILE_ROOT', None)
        if not v2_delivery_file_root:
            self.stderr.write('WARNING: settings.DEVILRY_V2_DELIVERY_FILE_ROOT is not set,'
                              'so FileMeta will not be imported.')

        self.__abort_if_input_directory_does_not_exist()
        self.__verify_empty_database()
        self.__run()

    def __get_all_importer_classes(self):
        return [
            modelimporters.UserImporter,
            modelimporters.NodeImporter,
            modelimporters.SubjectImporter,
            modelimporters.PeriodImporter,
            modelimporters.AssignmentImporter,
            modelimporters.PointToGradeMapImporter,
            modelimporters.PointRangeToGradeImporter,
            modelimporters.RelatedExaminerImporter,
            modelimporters.RelatedStudentImporter,
            modelimporters.AssignmentGroupImporter,
            modelimporters.ExaminerImporter,
            modelimporters.CandidateImporter,
            modelimporters.FeedbackSetImporter,
            modelimporters.DeliveryImporter,
            modelimporters.StaticFeedbackImporter,
            modelimporters.FileMetaImporter,
            modelimporters.CommentFileContentImporter,
            modelimporters.StatusImporter,
            modelimporters.QualifiesForFinalExamImporter
        ]

    def __get_all_importer_classnames(self):
        return [cls.__name__ for cls in self.__get_all_importer_classes()]

    def __get_importer_classes(self):
        found_start = True
        if self.start_at_importer_classname:
            found_start = False
        final_importer_classes = []
        for importer_class in self.__get_all_importer_classes():
            if self.start_at_importer_classname and importer_class.__name__ == self.start_at_importer_classname:
                found_start = True
            if found_start:
                final_importer_classes.append(importer_class)
            if self.stop_at_importer_classname and importer_class.__name__ == self.stop_at_importer_classname:
                break
        return final_importer_classes

    def __iterate_importers(self):
        for importer_class in self.__get_importer_classes():
            yield importer_class(input_root=self.input_directory)

    def __verify_empty_database(self):
        if self.fake:
            return
        for importer in self.__iterate_importers():
            if importer.target_model_has_objects():
                self.stdout.write('{} objects already exists in the database. Aborting.'.format(
                    importer.prettyformat_model_name()))

    def __run(self):
        importer_classes = self.__get_importer_classes()
        for index, importer in enumerate(self.__iterate_importers(), start=1):
            self.stdout.write('Importing {index}/{count} {importer!r} - model: {model!r}'.format(
                importer=importer.__class__.__name__,
                index=index,
                count=len(importer_classes),
                model=importer.prettyformat_model_name()))
            with TimeExecution(importer.prettyformat_model_name(), self):
                with transaction.atomic():
                    try:
                        importer.import_models(fake=self.fake)
                    except:
                        self.stderr.write(
                            '{!r} failed. Revering changes for this importer. '
                            'You can re-run from this point on with '
                            '"--start-at {}"'.format(importer.prettyformat_model_name(),
                                                     importer.__class__.__name__))
                        raise
