from devilry.devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .post_statussave import post_statussave
from .summarygenerator import make_settings_summary_points



qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_points',
    url = reverse_lazy('devilry_qualifiesforexam_points'),
    title = _('Students must get a minimum number of points'),
    description = _('Choose this option if you require your students to get a minimum number of points in total on all or some of their assignments to qualify for final exams. You select the assignments on the next page.'),
    post_statussave = post_statussave,
    pluginsettings_summary_generator = make_settings_summary_points,
    uses_settings = True
)
