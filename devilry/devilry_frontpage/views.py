from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


class FrontpageView(TemplateView):
    template_name = 'devilry_frontpage/frontpage.django.html'

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        user_model = get_user_model()
        context['user_is_student'] = user_model.objects.user_is_student(self.request.user)
        context['user_is_examiner'] = user_model.objects.user_is_examiner(self.request.user)
        user_is_any_admin = user_model.objects.user_is_admin_or_superuser(self.request.user)
        context['user_is_any_admin'] = user_is_any_admin
        return context


frontpage = login_required(FrontpageView.as_view())
