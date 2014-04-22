from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView

from devilry.apps.core.models.devilryuserprofile import user_is_student
from devilry.apps.core.models.devilryuserprofile import user_is_examiner
from devilry.apps.core.models.devilryuserprofile import user_is_assignmentadmin
from devilry.apps.core.models.devilryuserprofile import user_is_periodadmin
from devilry.apps.core.models.devilryuserprofile import user_is_subjectadmin
from devilry.apps.core.models.devilryuserprofile import user_is_nodeadmin



class AppView(Extjs4AppView):
    template_name = "devilry_frontpage/app.django.html"
    appname = 'devilry_frontpage'
    title = _('Devilry - Frontpage')


old_frontpage = login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view())))




class FrontpageView(TemplateView):
    template_name = 'devilry_frontpage/frontpage.django.html'

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        context['user_is_student'] = user_is_student(self.request.user)
        context['user_is_examiner'] = user_is_examiner(self.request.user)
        user_is_any_subjectadmin = user_is_assignmentadmin(self.request.user) \
            or user_is_periodadmin(self.request.user) \
            or user_is_subjectadmin(self.request.user)
        context['user_is_any_subjectadmin'] = user_is_any_subjectadmin
        context['user_is_nodeadmin'] = user_is_nodeadmin(self.request.user)
        return context


frontpage = login_required(FrontpageView.as_view())
