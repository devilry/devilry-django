from devilry.devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .summarygenerator import make_settings_summary_points



qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_select',
    url = reverse_lazy('devilry_qualifiesforexam_select'),
    title = _('Select manually'),
    description = _('Choose this option if you want to select the students that qualify for final exams manually.'),
    pluginsettings_summary_generator = make_settings_summary_points,
    uses_settings = False
)
