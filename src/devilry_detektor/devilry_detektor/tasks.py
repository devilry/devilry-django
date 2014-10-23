from cStringIO import StringIO
from celery import task
from celery.utils.log import get_task_logger
import os

from devilry.apps.core.models import Delivery
from devilry_detektor.models import DetektorAssignment


logger = get_task_logger(__name__)


class RunDetektorOnDelivery(object):
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

    def __init__(self, delivery):
        self.delivery = delivery

    def _get_filetype_from_filename(self, filename):
        name, extension = os.path.splitext(filename)
        for filetype, extensions in self.SUPPORTED_FILE_TYPES.iteritems():
            if extension in extensions:
                return filetype
        return None

    def _group_filemetas_by_extension(self):
        filemetasinfo_by_filetype = {}
        for filemeta in self.delivery.filemetas.order_by('filename'):
            if filemeta.size > self.MAX_FILESIZE:
                logger.warning('Skipping filemeta with ID=%s due to size limit.', filemeta.id)
                continue
            filetype = self._get_filetype_from_filename(filemeta.filename)
            if filetype:
                if not filetype in filemetasinfo_by_filetype:
                    filemetasinfo_by_filetype[filetype] = {'filemetas': [], 'size': 0}
                filemetasinfo_by_filetype[filetype]['filemetas'].append(filemeta)
                filemetasinfo_by_filetype[filetype]['size'] += filemeta.size
        return filemetasinfo_by_filetype

    def _find_most_prominent_filetype_filemetas(self, filemetasinfo_by_filetype):
        """
        Order by total size of files descending order, and return the first.
        """
        filemetasinfolist = filemetasinfo_by_filetype.values()
        filemetasinfolist.sort(lambda a, b: cmp(b['size'], a['size']))
        return filemetasinfolist[0]['filemetas']

    def _merge_filemetas_into_single_fileobject(self, filemetas):
        merged_file = StringIO()
        for filemeta in filemetas:
            merged_file.write(filemeta.get_all_data_as_string())
        merged_file.seek(0)
        return merged_file

    def run_detektor(self):
        filemetasinfo_by_filetype = self._group_filemetas_by_filetype()
        if not filemetasinfo_by_filetype:
            return
        filemetas = self._find_most_prominent_filetype_filemetas(filemetasinfo_by_filetype)
        fileobject = self._merge_filemetas_into_single_fileobject(filemetas)
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
            .exclude(delivery_id__in=self.detektorassignment.detektordelivery_set.values_list('delivery_id'))\
            .prefetch_related('filemetas')
        for delivery in unprocessed_deliveries:
            self._process_delivery(delivery)

    def _process_delivery(self, delivery):
        process_delivery_runner = RunDetektorOnDelivery(delivery)
        process_delivery_runner.run_detektor()

@task()
def run_detektor_on_assignment(assignment_id):
    RunDetektorOnAssignment(assignment_id)
