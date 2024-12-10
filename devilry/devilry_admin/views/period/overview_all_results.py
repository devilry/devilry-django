# -*- coding: utf-8 -*-


import json

from django.utils.translation import gettext_lazy

from cradmin_legacy import crapp
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers.listbuilderview import FilterListMixin

from devilry.apps.core import models as core_models
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
from devilry.devilry_admin.views.period import overview_all_results_collector
from devilry.devilry_cradmin.devilry_tablebuilder import base_new
from devilry.devilry_report.models import DevilryReport
from devilry.devilry_report.views.download_report import DownloadReportView


class RelatedStudentItemValue(base_new.AbstractCellRenderer):
    """
    Cell-renderer for a ``RelatedStudent``.

    Used to render information about a student in a single cell. The ``RelatedStudent`` can be
    obtained in the template with ``me.related_student``.
    """
    template_name = 'devilry_admin/period/all_results_overview/student_cell_value.django.html'
    valuealias = 'relatedstudent'

    def __init__(self, related_student):
        self.related_student = related_student
        super(RelatedStudentItemValue, self).__init__()


class ResultItemValue(base_new.AbstractCellRenderer):
    """
    Cell-renderer for the result on an assignment for a ``RelatedStudent``.

    Renders general information about the assignment for a student.
    The result can be obtained in the template with ``me.assignment_result``. If the student
    has made a delivery on the assignment, and the delivery has been corrected, the assignment and the
    score can be obtained through ``me.assignment`` and ``me.points``.
    """
    template_name = 'devilry_admin/period/all_results_overview/result_cell_value.django.html'

    def __init__(self, assignment, related_student_result):
        self.assignment_result = ''
        if not related_student_result.student_is_registered_on_assignment(assignment_id=assignment.id):
            self.assignment_result = 'not-registered'
        elif related_student_result.is_waiting_for_deliveries(assignment_id=assignment.id):
            self.assignment_result = 'waiting-for-deliveries'
        elif related_student_result.no_deliveries_hard_deadline(assignment=assignment):
            self.assignment_result = 'no-deliveries'
        elif related_student_result.is_waiting_for_feedback(assignment_id=assignment.id):
            self.assignment_result = 'waiting-for-feedback'
        else:
            self.assignment = assignment
            self.points = related_student_result.get_result_for_assignment(assignment_id=assignment.id)
        super(ResultItemValue, self).__init__()


class ColumnHeader(base_new.AbstractCellRenderer):
    """
    Cell-renderer for the header-row.

    Renders some descriptive text for the column.
    """
    template_name = 'devilry_admin/period/all_results_overview/column_header_item.django.html'

    def __init__(self, header_text):
        self.header_text = header_text
        super(ColumnHeader, self).__init__()

    def get_extra_css_classes_list(self):
        css_classes_list = super(ColumnHeader, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-tabulardata-list__cell--columnheader')
        return css_classes_list


class StudentRowList(base_new.AbstractRowList):
    """
    Row-renderer for a ``RelatedStudent``.

    Adds a renderable structure to its ``renderable_list`` with information about the student and the results on
    each assignment. This must of course reflect the structure header row.
    """
    valuealias = 'related_student_results'

    def __init__(self, assignments, related_student_result):
        super(StudentRowList, self).__init__()

        # Add renderable for the student information (name etc).
        self.renderable_list.append(
            RelatedStudentItemValue(related_student=related_student_result.relatedstudent)
        )

        # Add a renderable for each assignment with access to the results.
        for assignment in assignments:
            self.renderable_list.append(
                ResultItemValue(assignment=assignment, related_student_result=related_student_result)
            )

    def get_extra_css_classes_list(self):
        css_classes_list = super(StudentRowList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-tabulardata-list__row--result-info')
        return css_classes_list


class ListAsTable(base_new.AbstractListAsTable):
    """
    A renderable list used as the table for the overview.

    Using a list as a table means that the list and renderables of the list is styled as
    table elements with css.
    """
    template_name = 'devilry_admin/period/all_results_overview/devilry_admin_all_results_overview_table.django.html'

    def __init__(self, assignments, collector, **kwargs):
        """
        Args:
            assignments (QuerySet): QuerySet of :class:`~.devilry.apps.core.models.Assignment` objects.

            collector (PeriodResultsCollector): instance of
                :obj:`~.devilry.devilry_admin.views.period.overview_all_results_collector.PeriodAllResultsCollector`
        """
        self.assignments = assignments
        self.collector = collector
        super(ListAsTable, self).__init__(**kwargs)

    def add_header(self):
        """
        Builds the header of the table.
        """
        if self.collector.has_students():
            self.append_header_renderable(ColumnHeader(header_text='Student'))
            for assignment in self.assignments:
                self.append_header_renderable(ColumnHeader(header_text=assignment.short_name))

    def add_rows(self):
        """
        Builds the "body" of the table. Each element(row) added is its own list with renderables.

        See :class:`~.StudentRowList`.
        """
        for related_student_result in list(self.collector.results.values()):
            self.append(StudentRowList(assignments=self.assignments, related_student_result=related_student_result))


class RelatedStudentsAllResultsOverview(FilterListMixin, listbuilderview.View):
    model = core_models.RelatedStudent
    template_name = "devilry_admin/period/all_results_overview/devilry_all_results_overview.django.html"

    def get_pagetitle(self):
        return gettext_lazy('All students results')

    def get_no_items_message(self):
        return gettext_lazy('No students on period')

    def get_filterlist_position(self):
        return 'top'

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())

    def get_listbuilder_list(self, context):
        period = self.request.cradmin_role
        student_ids = [relatedstudent.id for relatedstudent in self.get_listbuilder_list_value_iterable(context)]
        return ListAsTable(
            assignments=period.assignments.prefetch_point_to_grade_map().all().order_by('first_deadline'),
            collector=self.get_results_collector_class()(period=period, related_student_ids=student_ids),
            is_paginated=True,
            page_obj=context['page_obj']
        )

    def get_paginate_by(self, queryset):
        return 40

    def get_unfiltered_queryset_for_role(self, role):
        period = self.request.cradmin_role
        related_student_queryset = core_models.RelatedStudent.objects\
            .filter(period=period)
        return related_student_queryset

    def get_results_collector_class(self):
        """
        Get the results collector for the class.

        Returns:
            (:class:`~.devilry.devilry_admin.view.period.overview_all_results_collector.PeriodAllResultsCollector`):
                The collector class to be used.
        """
        return overview_all_results_collector.PeriodAllResultsCollector

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string}
        )

    def get_context_data(self, **kwargs):
        context = super(RelatedStudentsAllResultsOverview, self).get_context_data(**kwargs)
        context['report_options'] = json.dumps({
            'generator_type': 'semesterstudentresults',
            'generator_options': {
                'period_id': self.request.cradmin_role.id
            }
        })
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^all-results-overview$',
                  RelatedStudentsAllResultsOverview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^all-results-overview/filter/(?P<filters_string>.+)?$',
                  RelatedStudentsAllResultsOverview.as_view(),
                  name='filter'),
        crapp.Url(r'^download-report$',
                  DownloadReportView.as_view(),
                  name='download_report')
    ]
