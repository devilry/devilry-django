from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView



class AppView(Extjs4AppView):
    template_name = "devilry_frontpage/app.django.html"
    appname = 'devilry_frontpage'
    title = _('Devilry - Frontpage')


frontpage = login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view())))
