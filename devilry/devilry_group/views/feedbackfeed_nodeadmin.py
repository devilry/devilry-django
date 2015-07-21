from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp
from django.db.models import Q


class NodeAdminFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    TODO: Document
    """
    def _get_queryset_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        )

    def get_context_data(self, **kwargs):
        context = super(NodeAdminFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'nodeadmin'
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            NodeAdminFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]