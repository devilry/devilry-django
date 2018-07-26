from devilry.apps.core.models import Subject, Period
from devilry.devilry_group.models import GroupComment


class PeriodDelete(object):
    """
    """
    def __init__(self, exclude_period_start_after_datetime):
        self.exclude_period_start_after_datetime = exclude_period_start_after_datetime

    def get_subject_queryset(self):
        return Subject.objects\
            .exclude(periods__isnull=True)\
            .all()

    def get_period_queryset(self, subject):
        return Period.objects\
            .filter(parentnode_id=subject.id)\
            .exclude(start_time__gt=self.exclude_period_start_after_datetime)

    def __delete_comment_files_on_period(self, period):
        """
        Delete comment files for period.
        """
        print '\tDeleting files for {}'.format(period)
        group_comments = GroupComment.objects\
            .filter(feedback_set__group__parentnode__parentnode_id=period.id)
        for group_comment in group_comments:
            group_comment.delete_comment()

    def subject_has_periods(self, subject):
        return Period.objects.filter(parentnode_id=subject.id).exists()

    def start(self):
        for subject in self.get_subject_queryset():
            print 'Subject - {}'.format(subject)
            periods = self.get_period_queryset(subject=subject)
            for period in periods:
                print '\tPeriod - {}'.format(period)
                self.__delete_comment_files_on_period(period=period)
                print '\tDeleting period'.format(period)
                period.delete()
            if not Period.objects.filter(parentnode_id=subject.id).exists():
                print '\tDeleting empty subject'.format(subject)
                subject.delete()
