from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView



class AppView(Extjs4AppView):
    template_name = "devilry_frontpage/app.django.html"
    appname = 'devilry_frontpage'
    css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'
    title = _('Devilry - Frontpage')
