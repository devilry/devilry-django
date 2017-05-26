import os

from django.core.management.base import BaseCommand

from devilry.devilry_import_v2database import modelimporters


class Command(BaseCommand):
    args = '<output-directory>'
    help = 'Dump the entire database to a directory of json files.'

    def add_arguments(self, parser):
        parser.add_argument(
            'input-directory',
            help='The input directory - a directory created with '
                 '"devilry_dump_database_for_v3_migration" with Devilry 2.x.')
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
        self.__abort_if_input_directory_does_not_exist()
        self.__verify_empty_database()
        self.__run()

    def __get_importer_classes(self):
        return [
            modelimporters.UserImporter,
            modelimporters.NodeImporter,
            modelimporters.SubjectImporter,
            modelimporters.PeriodImporter,
            modelimporters.AssignmentImporter,
            modelimporters.RelatedExaminerImporter,
            modelimporters.RelatedStudentImporter,
            modelimporters.AssignmentGroupImporter,
            modelimporters.ExaminerImporter,
            modelimporters.CandidateImporter,
            modelimporters.FeedbackSetImporter,
            modelimporters.DeliveryImporter,
            modelimporters.StaticFeedbackImporter,
            modelimporters.FileMetaImporter,
        ]

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
            self.stdout.write('Importing model {index}/{count} {model!r}'.format(
                index=index,
                count=len(importer_classes),
                model=importer.prettyformat_model_name()))
            importer.import_models(fake=self.fake)
