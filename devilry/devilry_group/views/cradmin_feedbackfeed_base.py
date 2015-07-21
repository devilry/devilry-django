from django.views.generic import base


class FeedbackFeedBaseView(base.TemplateView):
    template_name = "devilry_group/feedbackfeed.django.html"
    def _get_queryset_for_group(self, group):
        raise NotImplementedError("Subclasses must implement _get_queryset_for_group(group)!")

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period
        context['comments'] = self._get_queryset_for_group(self.request.cradmin_role)
        return context
