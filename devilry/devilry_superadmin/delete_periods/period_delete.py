import arrow

from devilry.apps.core.models import Subject, Period
from devilry.devilry_group.models import GroupComment


class PeriodDelete(object):
    """
    Delete periods with end_time older than specified number of months ago.

    Will delete periods and all the underlying data. If all periods on a
    subject is deleted, the subject is deleted as well.
    """
    def __init__(self, end_time_older_than_datetime, log_info=False):
        """
        Args:
            end_time_older_than_datetime: Months ago from from now.
            log_info: Should log info.
        """
        self.end_time_older_than_datetime = end_time_older_than_datetime
        self.log_info = log_info

    def __get_subject_queryset(self):
        return Subject.objects\
            .exclude(periods__isnull=True)\
            .all()

    def __get_period_queryset(self, subject):
        return Period.objects\
            .filter(parentnode_id=subject.id)\
            .filter(end_time__lt=self.end_time_older_than_datetime)

    def __delete_comment_files_on_period(self, period):
        """
        Delete comment files for period.
        """
        self.print_info(info_string='\tDeleting files for {}'.format(period))
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

    def print_info(self, info_string):
        """
        Print information if `log_info` is ``True``.
        """
        if self.log_info:
            print(info_string)

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
            periods = list(self.get_periods(subject=subject))
            if len(periods) > 0:
                preview_str += 'Subject - {}\n'.format(subject.long_name, subject.short_name)
                for period in periods:
                    preview_str += '\t{}({} - {})\n'.format(period.long_name,
                                                            period.start_time.strftime('%Y-%m-%d %H:%M'),
                                                            period.end_time.strftime('%Y-%m-%d %H:%M'))
        return preview_str

    def delete(self):
        for subject in self.get_subjects():
            periods = list(self.get_periods(subject=subject))
            if len(periods) > 0:
                self.print_info(info_string='Subject - {}'.format(subject))
                for period in self.get_periods(subject=subject):
                    self.print_info(info_string='\tPeriod - {}'.format(period))
                    self.__delete_comment_files_on_period(period=period)
                    self.print_info(info_string='\tDeleting period'.format(period))
                    period.delete()
                if not Period.objects.filter(parentnode_id=subject.id).exists():
                    self.print_info(info_string='\tDeleting empty subject'.format(subject))
                    subject.delete()
                self.print_info(info_string='\n')
