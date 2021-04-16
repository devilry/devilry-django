# -*- coding: utf-8 -*-


from django import http
from django.contrib import messages
from django.db import models
from django.db import transaction
from django.db.models.functions import Concat, Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers import listbuilderview

import django_rq

from devilry.devilry_email.feedback_email import feedback_email
from devilry.apps.core import models as core_models
from devilry.devilry_cradmin.devilry_tablebuilder import base_new
from devilry.devilry_group.models import GroupComment


class AbstractExaminerCell(base_new.AbstractCellRenderer):
    def get_base_css_classes_list(self):
        return ['devilry-tabulardata-list__cell-examiner']


class GroupItemValue(AbstractExaminerCell):
    template_name = 'devilry_examiner/assignment/simple_group_bulk_feedback/group_cell_value.django.html'
    valuealias = 'assignment_group'

    def __init__(self, assignment_group):
        self.assignment_group = assignment_group
        self.candidates = assignment_group.candidates.all()
        self.assignment = assignment_group.parentnode
        super(GroupItemValue, self).__init__()


class GradeFormFieldItemValue(AbstractExaminerCell):
    template_name = 'devilry_examiner/assignment/simple_group_bulk_feedback/grade_cell_value.django.html'

    def __init__(self, assignment_group):
        self.assignment = assignment_group.parentnode
        self.field_name = 'grade_{}'.format(assignment_group.id)
        super(GradeFormFieldItemValue, self).__init__()

    def get_context_data(self, request=None):
        context_data = super(GradeFormFieldItemValue, self).get_context_data(request=request)
        context_data['assignment'] = self.assignment
        context_data['assignment_uses_passed_failed_plugin'] = \
            self.assignment.grading_system_plugin_id == self.assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED
        return context_data


class CommentTextFormFieldItemValue(AbstractExaminerCell):
    template_name = 'devilry_examiner/assignment/simple_group_bulk_feedback/text_cell_value.django.html'

    def __init__(self, assignment_group_id):
        self.field_name = 'comment_text_{}'.format(assignment_group_id)
        super(CommentTextFormFieldItemValue, self).__init__()


class ColumnHeader(AbstractExaminerCell):
    template_name = 'devilry_examiner/assignment/simple_group_bulk_feedback/column_header_item.django.html'

    def __init__(self, header_text):
        self.header_text = header_text
        super(ColumnHeader, self).__init__()

    def get_extra_css_classes_list(self):
        css_classes_list = super(ColumnHeader, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-tabulardata-list__cell-examiner--columnheader')
        return css_classes_list


class GroupRowList(base_new.AbstractRowList):
    def __init__(self, assignment_group):
        self.assignment_group = assignment_group
        super(GroupRowList, self).__init__()
        self.append(GroupItemValue(assignment_group=self.assignment_group))
        self.append(GradeFormFieldItemValue(assignment_group=assignment_group))
        self.append(CommentTextFormFieldItemValue(assignment_group_id=assignment_group.id))


class ListAsTable(base_new.AbstractListAsTable):
    def __init__(self, assignment_groups, assignment, **kwargs):
        self.assignment_groups = assignment_groups
        self.assignment = assignment
        super(ListAsTable, self).__init__(**kwargs)

    def add_header(self):
        self.append_header_renderable(ColumnHeader(header_text=gettext_lazy('Students in groups')))
        self.append_header_renderable(ColumnHeader(header_text=gettext_lazy('Grading')))
        self.append_header_renderable(ColumnHeader(header_text=gettext_lazy('Comment text')))

    def add_rows(self):
        for group in self.assignment_groups:
            self.append(GroupRowList(assignment_group=group))


class SimpleGroupBulkFeedbackView(listbuilderview.View):
    model = core_models.AssignmentGroup
    template_name = 'devilry_examiner/assignment/simple_group_bulk_feedback/simple_group_bulk_feedbackview.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        return super(SimpleGroupBulkFeedbackView, self).dispatch(request, *args, **kwargs)

    def __get_candidate_queryset(self):
        return core_models.Candidate.objects\
            .select_related('relatedstudent__user')\
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__active',
                'relatedstudent__user__shortname',
                'relatedstudent__user__fullname'
            )\
            .order_by(
                Lower(
                    Concat(
                        'relatedstudent__user__fullname',
                        'relatedstudent__user__shortname',
                        output_field=models.CharField()
                    )))

    def get_queryset_for_role(self, role):
        return core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=self.request.user)\
            .filter(parentnode=role)\
            .exclude(cached_data__last_published_feedbackset=models.F('cached_data__last_feedbackset'))\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self.__get_candidate_queryset()))\
            .select_related(
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset',
                'parentnode',
                'parentnode__parentnode',
                'parentnode__parentnode__parentnode'
            )

    def get_listbuilder_list(self, context):
        queryset = self.get_queryset_for_role(role=self.request.cradmin_role)
        return ListAsTable(
            assignment_groups=queryset,
            assignment=self.assignment
        )

    def convert_grading_from_form_value(self, assignment, grade_from_form):
        """
        Converts the grading to points based on the grading plugin used.

        Args:
            assignment: Assignment with grading plugin info.
            grade_from_form: Grade posted in form.

        Returns:
            (int): grading as an integer.
        """
        if assignment.grading_system_plugin_id == assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            if grade_from_form == 'Failed':
                return 0
            return assignment.max_points
        if assignment.grading_system_plugin_id == assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return int(grade_from_form)

    def __collect_data_for_groups(self, posted_data):
        """
        Collects data by parsing the form fields.

        Args:
            posted_data: Posted form with fields to parse.

        Returns:
            (dict): Dictionary with instances of :class:`~.devilry.devilry_group.models.FeedbackSet`s as keys.
        """
        queryset = self.get_queryset()
        feedbackset_dict = {}
        for group in queryset:
            grade = posted_data.get('grade_{}'.format(group.id))
            comment_text = posted_data.get('comment_text_{}'.format(group.id))
            if len(grade) > 0:
                grade = self.convert_grading_from_form_value(assignment=self.assignment, grade_from_form=grade)
                feedbackset_dict[group.cached_data.last_feedbackset] = {
                    'grading_points': grade,
                    'comment_text': comment_text
                }
        return feedbackset_dict

    def __create_grading_groupcomment(self, feedbackset_id, published_time, text):
        """
        Creates a new :class:`~.devilry.devilry_group.models.GroupComment` with feedback.

        Args:
            feedbackset_id: Comment for.
            published_time: Comment published.
            text: Feedback text.
        """
        GroupComment.objects.create(
            feedback_set_id=feedbackset_id,
            part_of_grading=True,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            user=self.request.user,
            user_role=GroupComment.USER_ROLE_EXAMINER,
            text=text,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            published_datetime=published_time
        )

    def __publish(self, feedbackset_data_dict):
        """
        Creates :class:`~.devilry.devilry_group.models.GroupComment`s for the feedback if the textfield is filled and
        publishes the :class:`~.devilry.devilry_group.models.FeedbackSet`s.

        Note:
            Using ``transaction.atomic()`` for single transaction when creating comments and publishes feedbacks.
            If anything goes wrong, the transaction is rolled back and nothing is saved to the database.

        Args:
            feedbackset_data_dict: dictionary of ``FeedbackSet``s with posted comment data and points.
        """
        now_without_microseconds = timezone.now().replace(microsecond=0)
        feedbackset_id_list = []
        with transaction.atomic():
            for feedbackset, data in feedbackset_data_dict.items():
                text = data['comment_text']
                if len(text) > 0:
                    self.__create_grading_groupcomment(feedbackset.id, now_without_microseconds, text)
                feedbackset.grading_published_by = self.request.user
                feedbackset.grading_published_datetime = now_without_microseconds + timezone.timedelta(microseconds=1)
                feedbackset.grading_points = data['grading_points']
                feedbackset.save(update_fields=['grading_published_by', 'grading_published_datetime', 'grading_points'])
                feedbackset_id_list.append(feedbackset.id)
            feedback_email.bulk_send_feedback_created_email(
                assignment_id=self.assignment.id,
                feedbackset_id_list=feedbackset_id_list,
                domain_url_start=self.request.build_absolute_uri('/'))

    def post(self, request, *args, **kwargs):
        feedbackset_data_dict = self.__collect_data_for_groups(posted_data=request.POST)
        if feedbackset_data_dict:
            self.__publish(feedbackset_data_dict)
            messages.success(request,
                             message=gettext_lazy('Feedback published for {} groups').format(
                                 len(list(feedbackset_data_dict.keys()))))
        else:
            messages.warning(request, message=gettext_lazy('You must set a grade for at least one group.'))
        return http.HttpResponseRedirect(str(
            self.request.cradmin_app.reverse_appurl(viewname='bulk-feedback-simple')
        ))

    def get_context_data(self, **kwargs):
        context_data = super(SimpleGroupBulkFeedbackView, self).get_context_data(**kwargs)
        context_data['assignment'] = self.assignment
        context_data['assignment_uses_passed_failed_plugin'] = \
            self.assignment.grading_system_plugin_id == self.assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED
        return context_data

    def get_pagetitle(self):
        return gettext_lazy('Simple bulk feedback')

    def get_no_items_message(self):
        return gettext_lazy('No groups to receive feedback')
