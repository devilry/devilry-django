from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView

class AppView(Extjs4AppView):
    template_name = "devilry_nodeadmin/app.django.html"
    appname = 'devilry_nodeadmin'
    css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'
    title = _('Devilry - Node administrator')
