from django.utils.translation import ugettext_lazy as _
from devilry.devilry_extjsextras.views import DevilryExtjs4AppView


class AppView(DevilryExtjs4AppView):
    template_name = "devilry_subjectadmin/app.django.html"
    appname = 'devilry_subjectadmin'
    title = _('Devilry - Subject administrator')
