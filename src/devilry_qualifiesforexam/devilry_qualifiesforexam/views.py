from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView


class AppView(Extjs4AppView):
    template_name = "devilry_qualifiesforexam/app.django.html"
    appname = 'devilry_qualifiesforexam'
    title = _('Devilry - Qualifies for final exam')
