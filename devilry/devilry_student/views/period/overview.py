from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment
from devilry.devilry_cradmin import devilry_listbuilder


class GroupItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME,
        )

    def get_extra_css_classes_list(self):
        return ['devilry-student-listbuilder-grouplist-itemframe']


class PeriodOverviewView(listbuilderview.FilterListMixin,
                         listbuilderview.View):
    model = coremodels.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.StudentItemValue
    frame_renderer_class = GroupItemFrame
    paginate_by = 15
    template_name = 'devilry_student/period/overview.django.html'

    def get_value_and_frame_renderer_kwargs(self):
        kwargs = super(PeriodOverviewView, self).get_value_and_frame_renderer_kwargs()
        kwargs['include_periodpath'] = False
        return kwargs

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label=ugettext_lazy('Search'),
            label_is_screenreader_only=True,
            modelfields=[
                'parentnode__long_name',
                'parentnode__short_name',
                'parentnode__parentnode__long_name',
                'parentnode__parentnode__short_name',
                'parentnode__parentnode__parentnode__long_name',
                'parentnode__parentnode__parentnode__short_name',
            ]))

    def get_unfiltered_queryset_for_role(self, role):
        period = role
        return coremodels.AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .annotate_with_grading_points()\
            .annotate_with_is_waiting_for_feedback()\
            .annotate_with_is_waiting_for_deliveries()\
            .annotate_with_is_corrected()\
            .annotate_with_number_of_commentfiles_from_students()\
            .annotate_with_number_of_groupcomments_from_students()\
            .annotate_with_number_of_groupcomments_from_examiners()\
            .annotate_with_number_of_imageannotationcomments_from_students()\
            .annotate_with_number_of_imageannotationcomments_from_examiners()\
            .distinct()\
            .order_by('-parentnode__first_deadline', '-parentnode__publishing_time')\
            .prefetch_assignment_with_points_to_grade_map(
                assignmentqueryset=Assignment.objects.select_related('parentnode__parentnode'))

    def get_no_items_message(self):
        return pgettext_lazy('student period overview',
                             'No assignments.')

    def get_context_data(self, **kwargs):
        context = super(PeriodOverviewView, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<filters_string>.+)?$$',
                  PeriodOverviewView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]


# from django_cradmin.viewhelpers import objecttable
# from django_cradmin import crapp
# from django_cradmin import crinstance
# from django.utils.translation import ugettext_lazy as _
#
# from devilry.apps.core.models import AssignmentGroup
# from devilry.devilry_student.cradminextensions import studentobjecttable
#
#
# class LongNameColumn(objecttable.SingleActionColumn):
#     modelfield = 'id'
#     normalcells_css_classes = ['objecttable-cell-strong']
#
#     def get_header(self):
#         return _('Name')
#
#     def render_value(self, group):
#         return group.parentnode.long_name
#
#     def get_actionurl(self, group):
#         # return crinstance.reverse_cradmin_url(
#         #     instanceid='devilry_student_group',
#         #     appname='overview',
#         #     roleid=group.id)
#         return '#'
#
#     def is_sortable(self):
#         return False
#
#
# # class LastDeadlineColumn(objecttable.DatetimeColumn):
# #     orderingfield = 'last_deadline_datetime'
# #     modelfield = 'last_deadline_datetime'
# #
# #     def get_header(self):
# #         return _('Deadline')
# #
# #     def is_sortable(self):
# #         return False
#
#
# class StatusColumn(objecttable.Column):
#     template_name = 'devilry_student/cradmin_period/assignmentsapp/statuscolumn.django.html'
#     context_value_name = 'status'
#     context_object_name = 'group'
#     column_width = '250px'
#
#     def get_header(self):
#         return _('Status')
#
#     def render_value(self, group):
#         return group.get_status()
#
#
# class AssignmentGroupListView(studentobjecttable.StudentObjectTableView):
#     model = AssignmentGroup
#     template_name = 'devilry_student/cradmin_period/assignmentsapp/assignmentgroup-list.django.html'
#     columns = [
#         LongNameColumn,
#         # LastDeadlineColumn,
#         StatusColumn,
#     ]
#
#     def get_context_data(self, **kwargs):
#         context = super(AssignmentGroupListView, self).get_context_data(**kwargs)
#         context['period'] = self.request.cradmin_role
#         return context
#
#     def get_queryset_for_role(self, period):
#         return AssignmentGroup.objects\
#             .filter(parentnode__parentnode=period)\
#             .filter_student_has_access(user=self.request.user)\
#             .annotate_with_last_deadline_datetime()\
#             .extra(
#                 order_by=['-last_deadline_datetime']
#             )\
#             .select_related(
#                 'parentnode',  # Assignment
#                 'parentnode__parentnode',  # Period
#                 'parentnode__parentnode__parentnode'  # Subject
#             )
#
#
# class App(crapp.App):
#     appurls = [
#         crapp.Url(
#             r'^$',
#             AssignmentGroupListView.as_view(),
#             name=crapp.INDEXVIEW_NAME),
#     ]
