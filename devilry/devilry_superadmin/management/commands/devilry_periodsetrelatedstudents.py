from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from devilry.apps.core.models import Assignment
from devilry.devilry_compressionutil.models import CompressedArchiveMeta
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_superadmin.management.commands.devilry_periodsetrelatedexaminers import RelatedBaseCommand


class Command(RelatedBaseCommand):
    help = ('Set related students on a period. Users are read from stdin, as '
            'a JSON encoded array of arguments to the RelatedStudent model. '
            'See devilry/apps/superadmin/examples/relatedstudents.json for '
            'an example. If the period contains RelatedStudents with candidate_id '
            '(before or after the import), all CompressedArchiveMetas related to '
            'the period is marked for deletion.')

    @property
    def user_type(self):
        return "student"

    @property
    def related_user_model_class(self):
        from devilry.apps.core.models import RelatedStudent
        return RelatedStudent

    def _remove_compressed_archives_within_period(self):
        deleted_count = 0
        
        assignment_ids = Assignment.objects.filter(parentnode=self.period).values_list('id', flat=True)
        assignment_archives_queryset = CompressedArchiveMeta.objects\
            .filter(content_object_id__in=assignment_ids,
                    content_type=ContentType.objects.get_for_model(model=Assignment),
                    deleted_datetime=None)
        deleted_count += assignment_archives_queryset.count()
        assignment_archives_queryset.update(deleted_datetime=timezone.now())

        feedbackset_ids = FeedbackSet.objects.filter(group__parentnode__parentnode=self.period).values_list('id', flat=True)
        feedbackset_archives_queryset = CompressedArchiveMeta.objects\
            .filter(content_object_id__in=feedbackset_ids,
                    content_type=ContentType.objects.get_for_model(model=FeedbackSet),
                    deleted_datetime=None)
        deleted_count += feedbackset_archives_queryset.count()
        feedbackset_archives_queryset.update(deleted_datetime=timezone.now())

        return deleted_count

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.get_subject_and_period()

        candidate_id_set_before = set(
            self.related_user_model_class.objects
                .filter(period=self.period)
                .order_by('candidate_id')
                .distinct('candidate_id')
                .values_list('candidate_id', flat=True))

        with transaction.atomic():
            self.add_users()

            candidate_id_set_after = set(
                self.related_user_model_class.objects
                    .filter(period=self.period)
                    .order_by('candidate_id')
                    .distinct('candidate_id')
                    .values_list('candidate_id', flat=True))

            # If candidate IDs have changed, remove compressed archives within the period
            if candidate_id_set_before.difference(candidate_id_set_after):
                deleted_count = self._remove_compressed_archives_within_period()

                if self.verbosity > 1:
                    self.stdout.write(f'Marked {deleted_count} CompressedArchiveMetas for deletion because of candidate ID changes.')
