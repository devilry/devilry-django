from django.db import models
from django.db.models.functions import Lower, Concat
from django.utils.translation import pgettext, pgettext_lazy
from xml.sax.saxutils import quoteattr
from django.urls import reverse

from cradmin_legacy import crapp
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listbuilder

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Candidate, Examiner
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_examiner.views.selfassign.utils import assignment_groups_available_for_self_assign


class ExaminerSelfAssignGroupItemValue(devilry_listbuilder.assignmentgroup.ExaminerItemValue):
    template_name = 'devilry_examiner/selfassign/selfassign-group-item-value.django.html'
    valuealias = 'group'

    def get_assignment(self):
        return self.group.parentnode

    @property
    def is_assigned_to_group(self):
        return Examiner.objects.filter(
            assignmentgroup=self.group,
            relatedexaminer__user=self.kwargs['request'].user
        ).exists()

    @property
    def selfassign_api_url(self):
        request = self.kwargs['request']
        return f'{request.scheme}://{request.get_host()}{reverse("devilry_examiner_selfassign_api", kwargs={"period_id": self.kwargs["period"].id})}'

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
                    'Add me'),
                'assignProgressText': pgettext(
                    'examiner selfassign group item value',
                    'Adding...'
                ),
                'unassignText': pgettext(
                    'examiner selfassign group item value',
                    'Remove me'),
                'unassignProgressText': pgettext(
                    'examiner selfassign group item value',
                    'Removing...'
                ),
                'unavailableText': pgettext(
                    'examiner selfassign group item value',
                    'UNAVAILABLE'
                )
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

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusRadioFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.AssignmentCheckboxFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.AssignedUnassignedRadioFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByDelivery())
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter())

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
            ) \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count() \
            .distinct() \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode') \
            .order_by(
                'cached_data__last_feedbackset__deadline_datetime'
            )
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
    
    def get_distinct_assignments_queryset(self):
        if not hasattr(self, '_distinct_assignment_ids'):
            self._distinct_assignment_ids = self.__get_unfiltered_queryset_for_role() \
                .values_list('parentnode_id', flat=True)
        return coremodels.Assignment.objects \
            .filter(id__in=self._distinct_assignment_ids) \
            .distinct() \
            .order_by('short_name')

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
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  SelfAssignGroupListView.as_view(),
                  name='filter')
    ]
