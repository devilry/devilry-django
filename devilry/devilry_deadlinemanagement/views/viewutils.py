# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.views.generic import View

from devilry.apps.core import models as core_models


class DeadlineManagementMixin(View):

    def get_pagetitle(self):
        return ''

    def get_pageheading(self):
        return ''

    def get_page_subheading(self):
        return ''

    def get_startapp_backlink_url(self):
        """
        Override this function to provide a URL back to the app this
        view was accessed from.

        Note:
            By default this just redirects to back to the apps index view.
        """
        return self.request.cradmin_app.reverse_appindexurl()

    def get_context_data(self, **kwargs):
        context_data = super(DeadlineManagementMixin, self).get_context_data(**kwargs)
        context_data['startapp_backlink_url'] = self.get_startapp_backlink_url()
        context_data['pagetitle'] = self.get_pagetitle()
        context_data['pageheading'] = self.get_pageheading()
        context_data['page_subheading'] = self.get_page_subheading()
        return context_data

    def get_candidate_queryset(self):
        return core_models.Candidate.objects\
            .select_related('relatedstudent__user')\
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__user__shortname',
                'relatedstudent__user__fullname',
            )

    def get_examiner_queryset(self):
        return core_models.Examiner.objects\
            .select_related('relatedexaminer__user')\
            .only(
                'relatedexaminer',
                'assignmentgroup',
                'relatedexaminer__automatic_anonymous_id',
                'relatedexaminer__user__shortname',
                'relatedexaminer__user__fullname',
            )

    def get_annotations_for_queryset(self, queryset):
        """
        Add annotations for the the queryset.
        This function is called in ``get_unfiltered_queryset_for_role()``

        Args:
            queryset (QuerySet): Add annotations to.

        Returns:
            (QuerySet): annotated queryset.
        """
        return queryset \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count()\
            .annotate_with_is_passing_grade_count()

    def get_queryset_for_role_filtered(self, role):
        queryset = self.request.cradmin_app.get_accessible_group_queryset()
        assignment = role
        return queryset\
            .filter(parentnode=assignment)\
            .prefetch_related(
                models.Prefetch(
                    'candidates',
                    queryset=self.get_candidate_queryset()))\
            .prefetch_related(
                models.Prefetch(
                    'examiners',
                    queryset=self.get_examiner_queryset()))\
            .select_related(
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset',
                'parentnode'
            )
