from django_cradmin import crapp
from django_cradmin import renderable
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers.listbuilder import base
from django_cradmin.viewhelpers.listbuilderview import FilterListMixin

from devilry.apps.core import models as core_models
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser
from devilry.devilry_admin.views.period import overview_all_results_collector


class AbstractCellRenderer(renderable.AbstractRenderableWithCss):
    """
    Abstract class for cells which cell-renderers should inherit from.
    """
    def get_base_css_classes_list(self):
        return ['devilry-tabulardata-list__cell']


class RelatedStudentItemValue(AbstractCellRenderer):
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


class ResultItemValue(AbstractCellRenderer):
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
        elif related_student_result.is_waiting_for_feedback(assignment_id=assignment.id):
            self.assignment_result = 'waiting-for-feedback'
        else:
            self.assignment = assignment
            self.points = related_student_result.get_result_for_assignment(assignment_id=assignment.id)
        super(ResultItemValue, self).__init__()


class ColumnHeader(AbstractCellRenderer):
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


class AbstractRowList(base.List):
    """
    Abstract class that inherits for ``base.List``.

    The subclasses that inherits from this has access to ``renderable_list`` where renderables can be added.
    """
    valuealias = 'related_student_results'
    template_name = 'devilry_admin/period/all_results_overview/base_row.django.html'


class StudentRowList(AbstractRowList):
    """
    Row-renderer for a ``RelatedStudent``.

    Adds a renderable structure to its ``renderable_list`` with information about the student and the results on
    each assignment. This must of course reflect the structure header row.
    """
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


class HeaderList(AbstractRowList):
    """
    Row-renderer for the header part of the table.
    """
    def __init__(self):
        super(HeaderList, self).__init__()
        
    
class ListAsTable(base.List):
    """
    A renderable list used as the table for the overview.

    Using a list as a table means that the list and renderables of the list is styled as
    table elements with css.
    """
    template_name = 'devilry_admin/period/all_results_overview/devilry_admin_all_results_overview_table.django.html'

    def __init__(self, assignments, collector, is_paginated=None, page_obj=None):
        """
        Args:
            is_paginated (bool): Should use pagination

            page_obj (django.core.paginator.Page): Page used for pagination.

            assignments (QuerySet): QuerySet of :class:`~.devilry.apps.core.models.Assignment` objects.

            collector (PeriodResultsCollector): instance of
                :obj:`~.devilry.devilry_admin.views.period.overview_all_results_collector.PeriodAllResultsCollector`

            header_renderable (:obj:`~.HeaderList`): A subclass of :class:`~.AbstractRowList`` to render
                the table header.
        """
        super(ListAsTable, self).__init__()
        self.is_paginated = is_paginated
        self.page_obj = page_obj
        self.assignments = assignments
        self.collector = collector
        self.header_renderable = HeaderList()

        # Build header
        self.__build_header()

        # Build body
        self.__build_student_result_row()

    def __build_header(self):
        """
        Builds the header of the table.
        """
        self.header_renderable.append(ColumnHeader(header_text='Students'))
        for assignment in self.assignments:
            self.header_renderable.append(ColumnHeader(header_text=assignment.short_name))

    def __build_student_result_row(self):
        """
        Builds the "body" of the table. Each element(row) added is its own list with renderables.

        See :class:`~.StudentRowList`.
        """
        for related_student_result in self.collector.results.values():
            self.append(StudentRowList(assignments=self.assignments, related_student_result=related_student_result))

    def get_context_data(self, request=None):
        context_data = super(ListAsTable, self).get_context_data(request=request)
        context_data['page_obj'] = self.page_obj
        context_data['is_paginated'] = self.is_paginated
        return context_data


class RelatedStudentsAllResultsOverview(FilterListMixin, listbuilderview.View):
    model = core_models.RelatedStudent
    template_name = "devilry_admin/period/all_results_overview/devilry_all_results_overview.django.html"
    max_before_pagination = 20

    def get_filterlist_position(self):
        return 'top'

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter_relateduser.Search())
        filterlist.append(listfilter_relateduser.OrderRelatedStudentsFilter())

    def get_listbuilder_list(self, context):
        period = self.request.cradmin_role
        student_ids = [relatedstudent.id for relatedstudent in self.get_listbuilder_list_value_iterable(context)]
        return ListAsTable(
            assignments=period.assignments.all().order_by('first_deadline'),
            collector=self.get_results_collector_class()(period=period, related_student_ids=student_ids),
            is_paginated=True,
            page_obj=context['page_obj']
        )

    def get_unfiltered_queryset_for_role(self, role):
        period = self.request.cradmin_role
        related_student_queryset = core_models.RelatedStudent.objects\
            .filter(period=period)
        if related_student_queryset.count() > self.max_before_pagination:
            self.paginate_by = 10
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


class App(crapp.App):
    appurls = [
        crapp.Url(r'^all-results-overview$', RelatedStudentsAllResultsOverview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^all-results-overview/filter/(?P<filters_string>.+)?$',
                  RelatedStudentsAllResultsOverview.as_view(),
                  name='filter')
    ]