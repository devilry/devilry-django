from cStringIO import StringIO
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import os

import detektor
from devilry.apps.core.models import Delivery
from devilry.devilry_detektor.models import DetektorAssignment
from devilry.devilry_detektor.models import DetektorDeliveryParseResult
from devilry.devilry_detektor.comparer import CompareManyCollection
from devilry.utils.devilry_email import send_message


logger = get_task_logger(__name__)


class FileMetaCollection(object):
    """
    A collection of FileMeta objects.
    """
    def __init__(self, language):
        self.language = language
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
    Collects filemetas and groups them by language.
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
        self.filemetacollection_by_language = {}
        for filemeta in filemetas:
            if filemeta.size > self.MAX_FILESIZE:
                logger.warning('Skipping filemeta with ID=%s due to size limit.', filemeta.id)
                continue
            self.add_filemeta(filemeta)

    def add_filemeta(self, filemeta):
        language = self._get_language_from_filename(filemeta.filename)
        if language:
            if not language in self.filemetacollection_by_language:
                self.filemetacollection_by_language[language] = FileMetaCollection(language)
            self.filemetacollection_by_language[language].add_filemeta(filemeta)

    def __len__(self):
        return len(self.filemetacollection_by_language)

    def __getitem__(self, language):
        return self.filemetacollection_by_language[language]

    def _get_language_from_filename(self, filename):
        name, extension = os.path.splitext(filename)
        for language, extensions in self.SUPPORTED_FILE_TYPES.iteritems():
            if extension in extensions:
                return language
        return None

    def get_filemetacollections_ordered_by_bytes(self):
        """
        Order by total size of files descending order, and
        Returns a list of :class:`.FileMetaCollection` objects ordered ascending by
        total size of the files in each collection.
        """
        filemetacollections = self.filemetacollection_by_language.values()
        filemetacollections.sort(lambda a, b: cmp(b.size, a.size))
        return filemetacollections

    def find_language_with_most_bytes(self):
        """
        Find the language with most bytes.
        """
        try:
            return self.get_filemetacollections_ordered_by_bytes()[0]
        except IndexError:
            return None


class DeliveryParser(object):
    def __init__(self, assignmentparser, delivery):
        self.assignmentparser = assignmentparser
        self.delivery = delivery
        self.filemetas_by_languages = FileMetasByFiletype(
            self.delivery.filemetas.order_by('filename'))

    def run_detektor(self):
        for filemetacollection in self.filemetas_by_languages.get_filemetacollections_ordered_by_bytes():
            parser = self.assignmentparser.get_detektor_parser(filemetacollection.language)
            parseresult = parser.make_parseresult(
                label='{language} code for delivery#{deliveryid}'.format(
                    language=filemetacollection.language,
                    deliveryid=self.delivery.id))
            for filemeta in filemetacollection.filemetas:
                parser.parse(parseresult, filemeta.get_all_data_as_string())
            parseresultmodel = DetektorDeliveryParseResult(
                delivery=self.delivery,
                language=filemetacollection.language,
                detektorassignment=self.assignmentparser.detektorassignment
            )
            parseresultmodel.from_parseresult(parseresult)
            parseresultmodel.save()


class AssignmentParser(object):
    """
    Parses all unparsed deliveries within an Assignment.
    The result is that all Deliveries within the Assignment
    has a corresponding DetektorDeliveryParseResult.
    """
    def __init__(self, assignment_id):
        self._parsers = {}
        self.assignment_id = assignment_id
        self.detektorassignment = DetektorAssignment.objects\
            .select_related('assignment')\
            .get(assignment_id=assignment_id)

    def run_detektor(self):
        logger.info('run_detektor_on_assignment on assignment: id=%s (%s)',
                    self.assignment_id, self.detektorassignment.assignment)
        self._process_deliveries()

    def get_detektor_parser(self, language):
        if language not in self._parsers:
            self._parsers[language] = detektor.parser.make_parser(language)
        return self._parsers[language]

    def get_unprocessed_delivery_queryset(self):
        return Delivery.objects\
            .filter(deadline__assignment_group__parentnode=self.detektorassignment.assignment)\
            .exclude(id__in=self.detektorassignment.parseresults.values_list('delivery', flat=True))\
            .prefetch_related('filemetas')

    def _process_deliveries(self):
        for delivery in self.get_unprocessed_delivery_queryset():
            self._process_delivery(delivery)

    def _process_delivery(self, delivery):
        process_delivery_runner = DeliveryParser(self, delivery)
        process_delivery_runner.run_detektor()


def _send_success_email(detektorassignment):
    assignmentpath = detektorassignment.assignment.get_path()
    message = render_to_string('devilry_detektor/admin/run_detektor_on_assignment_finished_email.django.txt', {
        'assignment': assignmentpath,
        'resulturl': u'{}{}'.format(
            settings.DEVILRY_SCHEME_AND_DOMAIN,
            reverse('devilry_detektor_admin_assignmentassembly',
                    kwargs={'assignmentid': detektorassignment.assignment.id}))
    })
    subject = _(u'Programming code similarity check processing for %(assignment)s is finished') % {
        'assignment': assignmentpath}
    send_message(
        subject, message, detektorassignment.processing_started_by)


@shared_task()
def run_detektor_on_assignment(assignment_id):
    assignmentparser = AssignmentParser(assignment_id)
    assignmentparser.run_detektor()
    logger.info('Comparing all detektor Parse results on assignment: id=%s (%s)',
                assignment_id, assignmentparser.detektorassignment.assignment)
    CompareManyCollection(assignmentparser.detektorassignment).save()
    _send_success_email(assignmentparser.detektorassignment)

    assignmentparser.detektorassignment.processing_finished_datetime = datetime.now()
    assignmentparser.detektorassignment.status = 'finished'
    assignmentparser.detektorassignment.save()
