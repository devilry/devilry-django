from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import Concat
from django.db.models.functions import Lower
from django.http import Http404
from django_cradmin import crapp
from django_cradmin.viewhelpers import detail

from devilry.apps.core.models import AssignmentGroup, Examiner, Candidate
from devilry.devilry_cradmin import devilry_listbuilder


class GroupDetailsRenderable(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue):
    template_name = 'devilry_admin/assignment/students/groupdetails/details-renderable.django.html'


class GroupDetailsView(detail.DetailView):
    template_name = 'devilry_admin/assignment/students/groupdetails/view.django.html'

    def get_queryset_for_role(self, role):
        assignment = role
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent__user')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        examinerqueryset = Examiner.objects\
            .select_related('relatedexaminer__user')\
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))
        return AssignmentGroup.objects\
            .filter(parentnode=assignment)\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=examinerqueryset))\
            .annotate_with_is_waiting_for_feedback_count()\
            .annotate_with_is_waiting_for_deliveries_count()\
            .annotate_with_is_corrected_count() \
            .annotate_with_number_of_private_groupcomments_from_user(user=self.request.user) \
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=self.request.user)\
            .distinct() \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode')

    def dispatch(self, request, *args, **kwargs):
        self.group = self.get_object()
        self.assignment = self.request.cradmin_role
        self.devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and self.devilryrole != 'departmentadmin':
            raise Http404()
        return super(GroupDetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GroupDetailsView, self).get_context_data(**kwargs)
        context['group'] = self.group
        context['groupdetails'] = GroupDetailsRenderable(
            value=self.group,
            assignment=self.assignment)
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<pk>\d+)$',
                  GroupDetailsView.as_view(),
                  name='groupdetails'),
    ]
