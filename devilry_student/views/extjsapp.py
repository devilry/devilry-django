from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView


class AppView(Extjs4AppView):
    template_name = "devilry_student/app.django.html"
    appname = 'devilry_student'
    css_staticpath = 'devilry_theme/resources/stylesheets/devilry.css'
    title = _('Devilry - Student')