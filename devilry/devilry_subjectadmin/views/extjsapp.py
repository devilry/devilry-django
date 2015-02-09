from django.utils.translation import ugettext_lazy as _
from extjs4.views import Extjs4AppView



class AppView(Extjs4AppView):
    template_name = "devilry_subjectadmin/app.django.html"
    appname = 'devilry_subjectadmin'
    #css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'
    #css_staticpath = 'extjs4/resources/css/ext-all-gray.css'
    title = _('Devilry - Subject administrator')
