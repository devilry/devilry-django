from django.db.models import Q
from django_cradmin import crapp
from django.views.generic import base
from devilry.devilry_group import models


class FeedbackFeedView(base.TemplateView):
    template_name = "devilry_group/cradmin_feedbackfeed.django.html"

    def __get_comments(self, user, group):
        return models.GroupComment.objects.filter(
            Q(feedback_set__published_datetime__isnull=False) | Q(instant_publish=True),
            visible_for_students=True,
            feedback_set__group=group
        )

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedView, self).get_context_data(**kwargs)
        context['comments'] = self.__get_comments(self.request.user, self.request.cradmin_role)
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            FeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]