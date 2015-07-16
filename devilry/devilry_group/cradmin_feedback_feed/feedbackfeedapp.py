from django_cradmin import crapp
from django.views.generic import base

class FeedbackFeedView(base.TemplateView):
    template_name = "devilry_group/cradmin_feedback_feed/feedbackfeed.django.html"

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedView, self).get_context_data(**kwargs)

        context['header_field_text'] = "Hello, I was set in the FeedbackFeedView's get_context_data function!"
        return context

class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            FeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]