# django imports
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

# Devilry/cradmin imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp

# 3rd party imports
from crispy_forms import layout


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """

    def _get_comments_for_group(self, group):
        """
        Filters the comments a student should have access to.
        A student should only be able to see comments
        with :obj:`devilry.devilry_group.models.AbstractGroupComment.visibility` set to :obj:`devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`.

        :param group:
            The :class:`devilry.apps.core.models.AssignmentGroup` the user belongs to.

        Returns:
            List of :class:`devilry.devilry_group.models.GroupComment` objects.
        """
        return models.GroupComment.objects.filter(
            Q(feedback_set__grading_published_datetime__isnull=False) |
            Q(visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE),
            visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            feedback_set__group=group
        ).exclude_is_part_of_grading_feedbackset_unpublished()

    def get_context_data(self, **kwargs):
        context = super(StudentFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'student'
        return context

    def get_buttons(self):
        return [
            layout.Submit(
                'student_add_comment',
                _('Add comment'),
                css_class='btn btn-success')
        ]

    def set_automatic_attributes(self, obj):
        super(StudentFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'student'
        obj.published_datetime = timezone.now()

    def save_object(self, form, commit=True):
        obj = super(StudentFeedbackFeedView, self).save_object(form)
        self._convert_temporary_files_to_comment_files(form, obj)
        if len(obj.text) > 0:
            obj = super(StudentFeedbackFeedView, self).save_object(form, commit=True)
        return obj


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
