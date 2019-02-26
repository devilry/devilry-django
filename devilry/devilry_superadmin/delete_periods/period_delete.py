# -*- coding: utf-8 -*-


import arrow
from django.utils import timezone

from devilry.apps.core.models import Subject, Period, Assignment, AssignmentGroup
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import GroupComment


class PeriodDelete(object):
    """
    Delete periods with end_time older than specified number of months ago.

    Will delete periods and all the underlying data. If all periods on a
    subject is deleted, the subject is deleted as well.
    """
    def __init__(self, end_time_older_than_datetime, delete_empty_subjects=False, log_info=False):
        """
        Args:
            end_time_older_than_datetime: Months ago from from now.
            log_info: Should log info.
            delete_empty_subjects: Delete subject if all periods are deleted.
        """
        self.end_time_older_than_datetime = end_time_older_than_datetime
        self.log_info = log_info
        self.delete_empty_subjects = delete_empty_subjects

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
        self.print_info(info_string='\t\t- Deleting files for {}'.format(period))
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

    def get_extra_preview_data(self, period):
        assignment_count = Assignment.objects.filter(parentnode=period).count()
        assignment_group_count = AssignmentGroup.objects.filter(parentnode__parentnode=period).count()
        group_comments = GroupComment.objects.filter(feedback_set__group__parentnode__parentnode=period)
        comment_file_count = CommentFile.objects\
            .filter(comment_id__in=group_comments.values_list('id', flat=True)).count()
        return '\t\t- Assignments: {}' \
               '\n\t\t- Assignment groups: {}' \
               '\n\t\t- Comments: {}' \
               '\n\t\t- Files: {}'.format(
            assignment_count,
            assignment_group_count,
            group_comments.count(),
            comment_file_count
        )

    def __get_prettified_datetime(self, datetime_obj):
        """
        Prettify datetime object with Arrow.
        """
        return arrow.get(datetime_obj.astimezone(timezone.get_current_timezone())).format('MMM D. YYYY HH:mm')

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
                    preview_str += '\t{} ({} - {})\n {}\n\n'.format(
                        period.long_name,
                        self.__get_prettified_datetime(period.start_time),
                        self.__get_prettified_datetime(period.end_time),
                        self.get_extra_preview_data(period=period))
        return preview_str

    def delete(self):
        for subject in self.get_subjects():
            periods = list(self.get_periods(subject=subject))
            if len(periods) > 0:
                self.print_info(info_string='Subject - {}'.format(subject))
                for period in self.get_periods(subject=subject):
                    self.print_info(info_string='\tSemester - {}'.format(period.short_name))
                    self.__delete_comment_files_on_period(period=period)
                    self.print_info(info_string='\t\t- Deleting semester')
                    period.delete()

                if self.delete_empty_subjects:
                    if not Period.objects.filter(parentnode_id=subject.id).exists():
                        self.print_info(info_string='\tDeleting empty subject')
                        subject.delete()
                self.print_info(info_string='\n')
