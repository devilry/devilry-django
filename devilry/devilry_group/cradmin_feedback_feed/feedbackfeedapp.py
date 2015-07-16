from django_cradmin import crapp
from django.views.generic import base

class FeedbackFeedView(base.TemplateView):
    template_name = "devilry_group/cradmin_feedback_feed/feedbackfeed.django.html"

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedView, self).get_context_data(**kwargs)

        context['assignment'] = "Oblig 2 - How to duck"
        context['subject'] = "DUCK1000 -"
        context['subject_name'] = "Introduction to Duck -"
        context['period'] = "Autumn 2015"
        context['comment_text'] = 'MySuperAmazingDoctorateThesisExtremePleaseTakeMeSeriously.pdf'
        return context

class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            FeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]