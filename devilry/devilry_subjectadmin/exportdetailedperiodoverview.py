from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from cStringIO import StringIO
import csv
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from devilry.apps.core.models import Period
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment


class ExportDetailedPeriodOverviewBase(object):
    #: Does the format support including warnings?
    supports_warnings = True

    def __init__(self, grouper, query, filenameprefix):
        self.grouper = grouper
        self.query = query
        self.filenameprefix = filenameprefix
        self.gradedetails = self.query.get('grade', 'all')
        self.download = self.query.get('download', False) == '1'
        self.export_all_details = self.gradedetails == 'all'

    def generate(self):
        self.add_header()
        if self.supports_warnings:
            if self.grouper.ignored_students_with_results:
                warning = 'Student has feedback, but is not registered on the period.'
                for aggregated_relstudentinfo in self.grouper.iter_students_with_feedback_that_is_candidate_but_not_in_related():
                    self.add_aggregated_relstudentinfo(aggregated_relstudentinfo, warning)

            if self.grouper.ignored_students:
                warning = 'Student is in a group, but is not registered on the period'
                for aggregated_relstudentinfo in self.grouper.iter_students_with_no_feedback_that_is_candidate_but_not_in_related():
                    self.add_aggregated_relstudentinfo(aggregated_relstudentinfo, warning)

        # All related students
        for aggregated_relstudentinfo in self.grouper.iter_relatedstudents_with_results():
            self.add_aggregated_relstudentinfo(aggregated_relstudentinfo)

    def get_headerlist(self):
        header = ['NAME', 'USERNAME']
        for assignment in self.grouper.iter_assignments():
            if self.export_all_details:
                for datatype in ('Grade', 'Points', 'Passing grade'):
                    header.append('{0} ({1})'.format(assignment.short_name, datatype))
            else:
                header.append(assignment.short_name)
        header.append('WARNINGS')
        return header

    def add_header(self):
        self.add_row(self.get_headerlist())

    def add_row(self, iterable):
        raise NotImplementedError()

    def strformat_is_passing_grade(self, is_passing_grade):
        if is_passing_grade:
            return 'Passed'
        else:
            return 'Failed'

    def format_feedback(self, feedback):
        if self.export_all_details:
            return [feedback.grade,
                    feedback.points,
                    self.strformat_is_passing_grade(feedback.is_passing_grade)]
        elif self.gradedetails == 'grade':
            return [feedback.grade]
        elif self.gradedetails == 'points':
            return [str(feedback.points)]
        elif self.gradedetails == 'is_passing_grade':
            return [self.strformat_is_passing_grade(feedback.is_passing_grade)]

    def get_fullname_utf8(self, user):
        full_name = user.get_profile().full_name
        if full_name:
            return full_name.encode('utf-8')
        else:
            return 'name-missing'

    def add_aggregated_relstudentinfo(self, aggregated_relstudentinfo, warning=''):
        user = aggregated_relstudentinfo.user
        row = [self.get_fullname_utf8(user), user.username]
        for column, grouplist in enumerate(aggregated_relstudentinfo.iter_groups_by_assignment()):
            # NOTE: There can be more than one group if the same student is in more than one
            #       group on an assignment - we select the "best" feedback.
            cells = None
            if len(grouplist) == 0:
                if self.export_all_details:
                    cells = ['Not registered on assignment']*3
                else:
                    cells = ['Not registered on assignment']
            else:
                feedback = grouplist.get_feedback_with_most_points()
                if feedback:
                    cells = self.format_feedback(feedback)
                else:
                    if self.export_all_details:
                        cells = ['NO-FEEDBACK']*3
                    else:
                        cells = ['NO-FEEDBACK']
            row.extend(cells)
        row.append(warning)
        self.add_row(row)

    def get_content_type(self):
        return 'text/plain'

    def get_output(self):
        raise NotImplementedError()

    def get_filename(self):
        raise NotImplementedError()

    def response(self):
        response = HttpResponse(self.get_output(), content_type=self.get_content_type())
        if self.download:
            response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.get_filename())
        return response


class ExportDetailedPeriodOverviewCsv(ExportDetailedPeriodOverviewBase):
    supports_warnings = True
    def __init__(self, *args, **kwargs):
        super(ExportDetailedPeriodOverviewCsv, self).__init__(*args, **kwargs)
        self.out = StringIO()
        self.csvwriter = csv.writer(self.out, dialect='excel')
        self.generate()

    def add_row(self, iterable):
        self.csvwriter.writerow(iterable)

    def get_output(self):
        return self.out.getvalue()

    def get_filename(self):
        return '{0}.csv'.format(self.filenameprefix)


class ExportDetailedPeriodOverviewXslx(ExportDetailedPeriodOverviewBase):
    supports_warnings = True
    def __init__(self, *args, **kwargs):
        super(ExportDetailedPeriodOverviewXslx, self).__init__(*args, **kwargs)
        self.workbook = Workbook()
        self.worksheet = self.workbook.get_active_sheet()
        self.worksheet.title = self.filenameprefix
        self.currentrow = 0
        self.generate()

    def add_header(self):
        headerlist = self.get_headerlist()
        self.add_row(headerlist)
        for cells in self.worksheet.columns:
            cell = cells[0]
            cell.style.font.bold = True
            colwidth = None
            if cell.column == 'A':
                colwidth = 30
            elif cell.column == 'B':
                colwidth = 13
            elif cell.value == 'WARNINGS':
                colwidth = 70
            else:
                if self.export_all_details:
                    colwidth = 18
                else:
                    colwidth = 13
            self.worksheet.column_dimensions[cell.column].width = colwidth


    def add_cell(self, column, value):
        cell = self.worksheet.cell(row=self.currentrow, column=column)
        cell.value = value

    def add_row(self, iterable):
        for column, value in enumerate(iterable):
            self.add_cell(column, value)
        self.currentrow += 1

    def get_output(self):
        return save_virtual_workbook(self.workbook)

    def get_content_type(self):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def get_filename(self):
        return '{0}.xlsx'.format(self.filenameprefix)



class ExportDetailedPeriodOverview(View):
    exporters = {
        'csv': ExportDetailedPeriodOverviewCsv,
        'xslx': ExportDetailedPeriodOverviewXslx
    }
    def get(self, request, id):
        qry = Period.where_is_admin_or_superadmin(self.request.user).filter(id=id)
        if len(qry) == 0:
            return HttpResponseForbidden()
        period = qry[0]

        format = self.request.GET.get('format', None)
        if not format:
            return HttpResponseBadRequest('format is required.')

        exporter = self.exporters.get(format)
        if not exporter:
            return HttpResponseBadRequest('Invalid format: {0}. Valid formats: {1!r}'.format(
                format, self.exporters.keys()))

        filenameprefix = period.get_path()
        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        return exporter(grouper, query=self.request.GET, filenameprefix=filenameprefix).response()
