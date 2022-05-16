from django.db import models
from django.db.models.functions import Lower, Concat
from django.utils.translation import pgettext, pgettext_lazy
from xml.sax.saxutils import quoteattr
from django.urls import reverse

from cradmin_legacy import crapp
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listbuilder

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Candidate, Examiner, RelatedExaminer
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.apps.core.models import period_tag
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_assignmentgroup
from devilry.devilry_examiner.views.selfassign.utils import assignment_groups_available_for_self_assign


class ExaminerSelfAssignGroupItemValue(devilry_listbuilder.assignmentgroup.ExaminerItemValue):
    template_name = 'devilry_examiner/selfassign/selfassign-group-item-value.django.html'
    valuealias = 'group'

    def get_assignment(self):
        return self.group.parentnode

    @property
    def is_assigned_to_group(self):
        # return self.group.is_examiner
        return Examiner.objects.filter(
            assignmentgroup=self.group,
            relatedexaminer__user=self.kwargs['request'].user
        ).exists()

    @property
    def selfassign_api_url(self):
        request = self.kwargs['request']
        return f'{request.scheme}://{request.get_host()}{reverse("devilry_examiner_selfassign_api", kwargs={"group_id": self.group.id})}'

    @property
    def attributes(self):
        if self.is_assigned_to_group:
            assign_status = 'assigned'
        else:
            assign_status = 'unassigned'
        attributes = ' '.join(
            f'{key}={quoteattr(value)}' for key, value in {
                'selfAssignApiUrl': self.selfassign_api_url,
                'assignmenGroupId': f'{self.group.id}',
                'assignStatus': assign_status,
                'assignText': pgettext(
                    'examiner selfassign group item value',
                    'Assign'),
                'unassignText': pgettext(
                    'examiner selfassign group item value',
                    'Unassign'),
                'updatingText': pgettext(
                    'examiner selfassign group item value',
                    'Updating'),
            }.items()
        )
        return attributes


class SelfAssignGroupListView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = coremodels.AssignmentGroup
    value_renderer_class = ExaminerSelfAssignGroupItemValue
    frame_renderer_class = listbuilder.itemframe.DefaultSpacingItemFrame
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.period = self.request.cradmin_role
        return super(SelfAssignGroupListView, self).dispatch(request, *args, **kwargs)

    def get_period(self):
        return self.period

    def get_filterlist_template_name(self):
        return 'devilry_examiner/selfassign/selfassign.django.html'

    def get_pagetitle(self):
        return pgettext_lazy(
            'examiner selfassign view',
            '%(period_name)s - self-assign'
        ) % {
            'period_name': self.period.long_name
        }

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'request': self.request,
            'period': self.period
        }

    # def __add_filterlist_items_anonymous_uses_custom_candidate_ids(self, filterlist):
    #     filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymousUsesCustomCandidateIds())
    #     filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymousUsesCustomCandidateIds())

    # def __add_filterlist_items_anonymous(self, filterlist):
    #     filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymous())
    #     filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymous())

    def __add_filterlist_items_not_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())

    def add_filterlist_items(self, filterlist):
        # if self.assignment.is_anonymous:
        #     if self.assignment.uses_custom_candidate_ids:
        #         self.__add_filterlist_items_anonymous_uses_custom_candidate_ids(filterlist=filterlist)
        #     else:
        #         self.__add_filterlist_items_anonymous(filterlist=filterlist)
        # else:
        self.__add_filterlist_items_not_anonymous(filterlist=filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.StatusRadioFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())
        if self.__has_multiple_examiners():
            filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())
        
        period = self.get_period()
        if period_tag.PeriodTag.objects.filter(period=period).exists():
            filterlist.append(listfilter_assignmentgroup.AssignmentGroupRelatedStudentTagSelectFilter(period=period))

    def get_unfiltered_queryset_for_role(self, role):
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent__user')\
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__user__shortname',
                'relatedstudent__active',
                'relatedstudent__user__fullname',
            )\
            .order_by(
                Lower(
                    Concat(
                        'relatedstudent__user__fullname',
                        'relatedstudent__user__shortname',
                        output_field=models.CharField()
                    )))
        examinerqueryset = Examiner.objects\
            .select_related('relatedexaminer__user')\
            .only(
                'relatedexaminer',
                'assignmentgroup',
                'relatedexaminer__automatic_anonymous_id',
                'relatedexaminer__user__shortname',
                'relatedexaminer__user__fullname',
            )\
            .order_by(
                Lower(
                    Concat(
                        'relatedexaminer__user__fullname',
                        'relatedexaminer__user__shortname',
                        output_field=models.CharField()
                    )))
        queryset = assignment_groups_available_for_self_assign(period=role, user=self.request.user) \
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset)) \
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=examinerqueryset)) \
            .annotate(
                is_examiner=models.Exists(
                    Examiner.objects.filter(
                        relatedexaminer__user=self.request.user,
                        assignmentgroup_id=models.OuterRef('id')
                    )
                )
                # has_files=models.Exists(
                #     CommentFile.objects.filter(comment_id=models.OuterRef('id'))
                # )
            ) \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count() \
            .annotate_with_number_of_private_groupcomments_from_user(user=self.request.user) \
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=self.request.user) \
            .distinct() \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode')
        return queryset

    def __get_unfiltered_queryset_for_role(self):
        return self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role)

    def __get_total_groupcount(self):
        return self.__get_unfiltered_queryset_for_role().count()

    def __get_excluding_filters_other_than_status_is_applied(self, total_groupcount):
        return self.get_filterlist().filter(
            queryobject=self.__get_unfiltered_queryset_for_role(),
            exclude={'status'}
        ).count() < total_groupcount

    def get_filtered_all_students_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .count()

    def get_filtered_waiting_for_feedback_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_waiting_for_feedback__gt=0)\
            .count()

    def get_filtered_waiting_for_deliveries_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_waiting_for_deliveries__gt=0)\
            .count()

    def get_filtered_corrected_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_corrected__gt=0)\
            .count()

    def __get_distinct_relatedexaminer_ids(self):
        if not hasattr(self, '_distinct_relatedexaminer_ids'):
            self._distinct_relatedexaminer_ids = Examiner.objects\
                .filter(assignmentgroup__in=self.__get_unfiltered_queryset_for_role())\
                .values_list('relatedexaminer_id', flat=True)\
                .distinct()
            self._distinct_relatedexaminer_ids = list(self._distinct_relatedexaminer_ids)
        return self._distinct_relatedexaminer_ids

    def __has_multiple_examiners(self):
        return len(self.__get_distinct_relatedexaminer_ids()) > 1

    def get_distinct_relatedexaminers(self):
        return RelatedExaminer.objects\
            .filter(id__in=self.__get_distinct_relatedexaminer_ids())\
            .select_related('user')\
            .order_by(
                Lower(
                    Concat(
                        'user__fullname',
                        'user__shortname',
                        output_field=models.CharField()
                    )))

    def use_pagination_load_all(self):
        return True

    def get_context_data(self, **kwargs):
        context = super(SelfAssignGroupListView, self).get_context_data(**kwargs)
        total_groupcount = self.__get_total_groupcount()
        context['excluding_filters_other_than_status_is_applied'] = \
            self.__get_excluding_filters_other_than_status_is_applied(
                total_groupcount=total_groupcount)
        context['total_group_count'] = total_groupcount
        context['waiting_for_feedback_count'] = self.get_filtered_waiting_for_feedback_count()
        context['corrected_count'] = self.get_filtered_corrected_count()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  SelfAssignGroupListView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^/filter/(?P<filters_string>.+)?$',
                  SelfAssignGroupListView.as_view(),
                  name='filter')
    ]
