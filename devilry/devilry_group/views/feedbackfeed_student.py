from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp
from django.db.models import Q


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):

    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            Q(feedback_set__published_datetime__isnull=False) | Q(instant_publish=True),
            visible_for_students=True,
            feedback_set__group=group
        )

    def get_context_data(self, **kwargs):
        context = super(StudentFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'student'
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]