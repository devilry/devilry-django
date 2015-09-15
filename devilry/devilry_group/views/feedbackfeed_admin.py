from crispy_forms import layout
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crapp

from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models


class AdminFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    TODO: Document
    """
    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        )

    def get_buttons(self):
        return [
            layout.Submit(
                'administrator_add_comment',
                _('Add comment'),
                css_class='btn btn-success')
        ]

    def get_context_data(self, **kwargs):
        context = super(AdminFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'admin'
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AdminFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
