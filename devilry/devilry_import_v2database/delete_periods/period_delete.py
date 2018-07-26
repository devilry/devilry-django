from devilry.apps.core.models import Subject, Period
from devilry.devilry_group.models import GroupComment


class PeriodDelete(object):
    """
    Delete periods older than a specified datetime.

    Will delete periods and all the underlying data. If all periods on a
    subject is deleted, the subject is deleted as well.
    """
    def __init__(self, exclude_period_start_after_datetime):
        """
        Args:
            exclude_period_start_after_datetime: A datetime object, all periods
                with start_time after this is excluded.
        """
        self.exclude_period_start_after_datetime = exclude_period_start_after_datetime

    def __get_subject_queryset(self):
        return Subject.objects\
            .exclude(periods__isnull=True)\
            .all()

    def __get_period_queryset(self, subject):
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

    def get_subjects(self):
        """
        Get subject iterator.
        """
        for subject in self.__get_subject_queryset():
            yield subject

    def get_periods(self, subject):
        """
        Get period iterator.
        """
        for period in self.__get_period_queryset(subject=subject):
            yield period

    def get_preview(self):
        """
        Get a formatted preview over periods that will be deleted.

        Example of returned string::

            Subject - Subject 1
                Period 1
                Period 2
                Period 3

            Subject - Subject 2
                Period 1

        Returns:
            (str): Formatted string.
        """
        preview_str = ''
        for subject in self.get_subjects():
            preview_str += 'Subject - {}\n'.format(subject.long_name, subject.short_name)
            for period in self.get_periods(subject=subject):
                preview_str += '\t{}({} - {})\n'.format(period.long_name, period.start_time, period.end_time)
        return preview_str

    def delete(self):
        for subject in self.get_subjects():
            print 'Subject - {}'.format(subject)
            for period in self.get_periods(subject=subject):
                print '\tPeriod - {}'.format(period)
                self.__delete_comment_files_on_period(period=period)
                print '\tDeleting period'.format(period)
                period.delete()
            if not Period.objects.filter(parentnode_id=subject.id).exists():
                print '\tDeleting empty subject'.format(subject)
                subject.delete()
