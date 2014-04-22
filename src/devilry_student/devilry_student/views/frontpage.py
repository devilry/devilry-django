from django.views.generic import TemplateView


class FrontpageView(TemplateView):
    template_name = 'devilry_student/frontpage.django.html'

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        context['user_is_student'] = None
        return context