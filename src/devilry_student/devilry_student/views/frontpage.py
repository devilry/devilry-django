from django.views.generic import TemplateView

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Period


class FrontpageView(TemplateView):
    template_name = 'devilry_student/frontpage.django.html'

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)

        context['groups_waiting_for_deliveries'] = list(
            AssignmentGroup.objects\
                .filter_student_has_access(self.request.user)\
                .filter_is_active()\
                .filter_waiting_for_deliveries()\
                .select_related(
                    'last_deadline',
                    'parentnode', # Assignment
                    'parentnode__parentnode', # Period
                    'parentnode__parentnode__parentnode', # Subject
                )\
                .order_by('last_deadline__deadline')
        )

        active_periods = Period.objects\
            .filter_active()\
            .filter_is_candidate_or_relatedstudent(self.request.user)\
            .order_by('-start_time', 'parentnode__long_name', 'long_name')

        # active_periods = Period.objects\
        #     .filter_active()\
        #     .filter_is_candidate_or_relatedstudent(self.request.user)\
        #     .extra(
        #         select={
        #             'lastest_feedback_string': """
        #                 SELECT
        #                     core_assignment.short_name
        #                     || ","
        #                     || core_assignment.grading_system_plugin_id
        #                     || ","
        #                     || core_staticfeedback.is_passing_grade
        #                     || ","
        #                     || core_staticfeedback.grade
        #                 FROM core_assignment
        #                 INNER JOIN core_assignmentgroup ON (core_assignmentgroup.parentnode_id = core_assignment.id)
        #                 INNER JOIN core_deadline ON (core_deadline.assignment_group_id = core_assignmentgroup.id)
        #                 INNER JOIN core_delivery ON (core_delivery.deadline_id = core_deadline.id)
        #                 INNER JOIN core_staticfeedback ON (core_staticfeedback.delivery_id = core_delivery.id)
        #                 WHERE
        #                     core_assignment.parentnode_id = core_period.id
        #                     AND
        #                     core_assignmentgroup.delivery_status = "corrected"
        #                 ORDER BY core_staticfeedback.save_timestamp DESC
        #                 LIMIT 0,1
        #             """
        #         }
        #     )\
        #     .order_by('-start_time', 'parentnode__long_name', 'long_name')

        # for period in active_periods:
        #     if period.lastest_feedback_string:
        #         (assignment_short_name, grading_system_plugin_id,
        #          is_passing_grade, grade) = period.lastest_feedback_string.split(',', 3)
        #         period.latest_feedback_dict = {
        #             'assignment_short_name': assignment_short_name,
        #             'grading_system_plugin_id': grading_system_plugin_id,
        #             'is_passing_grade': int(is_passing_grade),
        #             'grade': grade
        #         }
        #         print period.latest_feedback_dict
                
        context['active_periods'] = active_periods

        return context