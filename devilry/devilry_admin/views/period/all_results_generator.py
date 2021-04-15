# -*- coding: utf-8 -*-


from django.utils import translation
from django.utils.translation import pgettext, gettext

from devilry.devilry_admin.views.period.overview_all_results_collector import PeriodAllResultsCollector
from devilry.devilry_email.utils import activate_translation_for_user
from devilry.devilry_report.abstract_generator import AbstractExcelReportGenerator
from devilry.apps.core.models import RelatedStudent, Assignment, Period


class AllResultsExcelReportGenerator(AbstractExcelReportGenerator):
    """
    Generates a downloadable Excel spreadsheet of all current student results.
    """
    def __init__(self, *args, **kwargs):
        super(AllResultsExcelReportGenerator, self).__init__(*args, **kwargs)
        self.period = Period.objects.get(id=self.generator_options['period_id'])

    @property
    def generator_options(self):
        return self.devilry_report.generator_options

    @classmethod
    def get_generator_type(cls):
        return 'semesterstudentresults'

    def get_output_filename_prefix(self):
        return '{}'.format(self.period.short_name)

    def get_object_iterable(self):
        related_student_queryset = RelatedStudent.objects \
            .filter(period=self.period)
        related_student_ids = [relatedstudent.id for relatedstudent in related_student_queryset]
        result_collector = PeriodAllResultsCollector(period=self.period, related_student_ids=related_student_ids)
        collected_results = [related_student_results for related_student_results in result_collector.results.values()]
        return collected_results

    def __get_all_assignments_for_period(self):
        """
        Fetch all assignments for the period.
        """
        return Assignment.objects.prefetch_point_to_grade_map()\
            .filter(parentnode_id=self.period.id)

    def add_worksheet_headers(self, worksheet):
        worksheet.write(0, 0, pgettext('devilry report semesters student results', 'Student'), self.header_cell_format)

        column_count = 1
        for assignment in self.__get_all_assignments_for_period().order_by('first_deadline'):
            worksheet.write(0, column_count, assignment.long_name, self.header_cell_format)
            column_count += 1

    def __get_student_status(self, related_student_result, assignment):
        if not related_student_result.student_is_registered_on_assignment(assignment.id):
            return pgettext('devilry report semesters assignment status', 'Not registered')
        elif related_student_result.is_waiting_for_deliveries(assignment.id):
            return pgettext('devilry report semesters assignment status', 'Waiting for deliveries')
        elif related_student_result.no_deliveries_hard_deadline(assignment):
            return pgettext('devilry report semesters assignment status', 'No deliveries')
        elif related_student_result.is_waiting_for_feedback(assignment.id):
            return pgettext('devilry report semesters assignment status', 'Waiting for feedback')
        return None

    def __write_data_to_grades_worksheet(self, worksheet, row, column, obj):
        """
        Write data to "Grades"-worksheet.
        """
        for assignment in self.__get_all_assignments_for_period().order_by('first_deadline'):
            result = self.__get_student_status(related_student_result=obj, assignment=assignment)
            if result:
                worksheet.write(row, column, result)
            else:
                points = obj.get_result_for_assignment(assignment.id)
                worksheet.write(row, column, '{}'.format(assignment.points_to_grade(points=points)))
            column += 1

    def __write_data_to_points_worksheet(self, worksheet, row, column, obj):
        """
        Write data to "Points"-worksheet.

        Writes empty- or `int`-value.
        """
        for assignment in self.__get_all_assignments_for_period().order_by('first_deadline'):
            result = self.__get_student_status(related_student_result=obj, assignment=assignment)
            if result:
                worksheet.write(row, column, '')
            else:
                points = obj.get_result_for_assignment(assignment.id)
                worksheet.write_number(row, column, points)
            column += 1

    def __write_data_to_passed_worksheet(self, worksheet, row, column, obj):
        """
        Write data to "Passed"-worksheet.

        Writes empty- or `boolean`-value.
        """
        for assignment in self.__get_all_assignments_for_period().order_by('first_deadline'):
            result = self.__get_student_status(related_student_result=obj, assignment=assignment)
            if result:
                worksheet.write(row, column, '')
            else:
                points = obj.get_result_for_assignment(assignment.id)
                worksheet.write_boolean(row, column, assignment.points_is_passing_grade(points=points))
            column += 1

    def write_data_to_worksheet(self, worksheet_tuple, row, column, obj):
        worksheet_type = worksheet_tuple[0]
        worksheet = worksheet_tuple[1]
        worksheet.write(row, column, obj.relatedstudent.user.get_short_name())
        column = 1

        if worksheet_type == 'grades':
            self.__write_data_to_grades_worksheet(worksheet=worksheet, row=row, column=column, obj=obj)
        elif worksheet_type == 'points':
            self.__write_data_to_points_worksheet(worksheet=worksheet, row=row, column=column, obj=obj)
        elif worksheet_type == 'passed':
            self.__write_data_to_passed_worksheet(worksheet=worksheet, row=row, column=column, obj=obj)

    def get_work_sheets(self):
        return [
            ('grades', self.workbook.add_worksheet(name=gettext('Grades'))),
            ('points', self.workbook.add_worksheet(name=gettext('Points'))),
            ('passed', self.workbook.add_worksheet(name=gettext('Passed Failed')))
        ]

    def generate(self, file_like_object):
        current_language = translation.get_language()
        activate_translation_for_user(user=self.devilry_report.generated_by_user)
        self.write(file_like_object=file_like_object)
        translation.activate(current_language)
