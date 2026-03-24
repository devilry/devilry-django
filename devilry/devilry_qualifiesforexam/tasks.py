import logging
import traceback

from django.db import transaction
from django.utils import timezone

from devilry.devilry_qualifiesforexam.models import DraftQualifiesForFinalExam, DraftStatus
from devilry.devilry_qualifiesforexam.utils.relatedstudent_queryset import get_relatedstudents_queryset

logger = logging.getLogger(__name__)


def generate_draft(collector_class, draft_status_id):
    try:
        draft_status = DraftStatus.objects.get(id=draft_status_id)
    except DraftStatus.DoesNotExist:
        logger.error("DraftStatus with id {} does not exist.".format(draft_status_id))
        return

    # Set starting status
    draft_status.processing_status = DraftStatus.ProcessingStatusChoices.IN_PROGRESS
    draft_status.processing_started_datetime = timezone.now()
    draft_status.save()

    # Run collector
    try:
        with transaction.atomic():
            collector = collector_class(period=draft_status.period, **draft_status.plugin_data)
            passing_relatedstudentids = collector.get_relatedstudents_that_qualify_for_exam()

            bulk_qualification_objects = []
            bulk_size = 200
            relatedstudent_queryset = get_relatedstudents_queryset(
                period=draft_status.period,
                extra_order_by_fields=["user__lastname"]
            )
            for relatedstudent in relatedstudent_queryset.iterator():
                bulk_qualification_objects.append(
                    DraftQualifiesForFinalExam(
                        draft_status=draft_status,
                        relatedstudent=relatedstudent,
                        qualifies=relatedstudent.id in passing_relatedstudentids,
                    )
                )
                if  len(bulk_qualification_objects) >= bulk_size:
                    DraftQualifiesForFinalExam.objects.bulk_create(bulk_qualification_objects)
                    bulk_qualification_objects.clear()

            # Create remaining objects
            if len(bulk_qualification_objects) > 0:
                DraftQualifiesForFinalExam.objects.bulk_create(bulk_qualification_objects)
    except Exception as e:
        logger.exception("Error while generating draft for DraftStatus with id {}.".format(draft_status_id))
        draft_status.processing_status = DraftStatus.ProcessingStatusChoices.ERROR
        draft_status.processing_status_data = {
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }
        draft_status.save()
    else:
        draft_status.processing_status = DraftStatus.ProcessingStatusChoices.COMPLETED
        draft_status.processing_completed_datetime = timezone.now()
        draft_status.save()