from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView



class AppView(Extjs4AppView):
    template_name = "devilry_frontpage/app.django.html"
    appname = 'devilry_frontpage'
    title = _('Devilry - Frontpage')


frontpage = login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view())))




class FrontpageView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        context['user_is_student'] = user_is_student()
        context['user_is_examiner'] = user_is_examiner()
        context['user_is_admin_or_superadmin'] = user_is_admin_or_superadmin()
        return context