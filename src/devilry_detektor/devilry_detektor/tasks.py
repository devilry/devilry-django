from cStringIO import StringIO
from celery import task
from celery.utils.log import get_task_logger
import os

import detektor
from devilry.apps.core.models import Delivery
from devilry_detektor.models import DetektorAssignment


logger = get_task_logger(__name__)


class FileMetaCollection(object):
    """
    A collection of FileMeta objects.
    """
    def __init__(self, filetype):
        self.filetype = filetype
        self.filemetas = []
        self.size = 0

    def add_filemeta(self, filemeta):
        self.filemetas.append(filemeta)
        self.size += filemeta.size

    def _merge_into_single_fileobject(self):
        merged_file = StringIO()
        for filemeta in self.filemetas:
            merged_file.write(filemeta.get_all_data_as_string())
        merged_file.seek(0)
        return merged_file


class FileMetasByFiletype(object):
    """
    Collects filemetas and groups them by filetype.
    """
    SUPPORTED_FILE_TYPES = {
        'java': {'.java'},
        'python': {'.py'},
        # 'c/cpp': {'.c', '.cxx', '.cpp', '.h', '.hxx', '.hpp'},
        # '.pl',
        # '.rb',
        # '.js',
        # '.c',
        # '.cpp',
        # '.cxx'
    }

    #: We do not send files larger than this to detektor
    MAX_FILESIZE = (2**20) * 10  # 10 MB

    def __init__(self, filemetas):
        self.filemetacollection_by_filetype = {}
        for filemeta in filemetas:
            if filemeta.size > self.MAX_FILESIZE:
                logger.warning('Skipping filemeta with ID=%s due to size limit.', filemeta.id)
                continue
            self.add_filemeta(filemeta)

    def add_filemeta(self, filemeta):
        filetype = self._get_filetype_from_filename(filemeta.filename)
        if filetype:
            if not filetype in self.filemetacollection_by_filetype:
                self.filemetacollection_by_filetype[filetype] = FileMetaCollection(filetype)
            self.filemetacollection_by_filetype[filetype].add_filemeta(filemeta)

    def __len__(self):
        return len(self.filemetacollection_by_filetype)

    def __getitem__(self, filetype):
        return self.filemetacollection_by_filetype[filetype]

    def _get_filetype_from_filename(self, filename):
        name, extension = os.path.splitext(filename)
        for filetype, extensions in self.SUPPORTED_FILE_TYPES.iteritems():
            if extension in extensions:
                return filetype
        return None

    def _get_filemetacollections_with_filetype_with_most_bytes_first(self):
        filemetacollections = self.filemetacollection_by_filetype.values()
        filemetacollections.sort(lambda a, b: cmp(b.size, a.size))
        return filemetacollections

    def _find_filetype_with_most_bytes(self):
        """
        Order by total size of files descending order, and return the first.
        """
        try:
            return self._get_filemetacollections_with_filetype_with_most_bytes_first()[0]
        except IndexError:
            return None


class RunDetektorOnDelivery(object):

    def __init__(self, delivery):
        self.delivery = delivery
        self.filemetas_grouped_by_filetype = FileMetasByFiletype(
            self.delivery.filemetas.order_by('filename'))

    # def _get_detektor_code_signature(self):
    #     filemetasinfo_by_filetype = self._group_filemetas_by_filetype()
    #     if not filemetasinfo_by_filetype:
    #         return
    #     filetype, filemetas = self._find_most_prominent_filetype_filemetas(filemetasinfo_by_filetype)
    #     fileobject = self._merge_filemetas_into_single_fileobject(filemetas)
    #     parser = detektor.libs.codeparser.Parser(filetype, fileobject)
    #     return parser.get_code_signature()

    def run_detektor(self):
        pass
        # Run detektor


class RunDetektorOnAssignment(object):
    def __init__(self, assignment_id):
        self.detektorassignment = DetektorAssignment.objects\
            .select_related('assignment')\
            .get(assignment_id=assignment_id)
        logger.info('run_detektor_on_assignment on assignment: id=%s (%s)',
                    assignment_id, self.detektorassignment.assignment)
        self._process_deliveries()
        self.detektorassignment.processing_started_datetime = None
        self.detektorassignment.save()

    def _process_deliveries(self):
        unprocessed_deliveries = Delivery.objects\
            .filter(deadline__assignment_group__parentnode=self.detektorassignment.assignment)\
            .exclude(delivery__in=self.detektorassignment.detektordelivery_set.values_list('delivery'))\
            .prefetch_related('filemetas')
        for delivery in unprocessed_deliveries:
            self._process_delivery(delivery)

    def _process_delivery(self, delivery):
        process_delivery_runner = RunDetektorOnDelivery(delivery)
        process_delivery_runner.run_detektor()

@task()
def run_detektor_on_assignment(assignment_id):
    RunDetektorOnAssignment(assignment_id)
