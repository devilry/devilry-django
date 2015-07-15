from django_cradmin import crapp
from django.views.generic import base

class FeedbackFeedView(base.TemplateView):
    template_name = "devilry_group/cradmin_feedback_feed/feedbackfeed.django.html"


#add SomeView here

class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            FeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]