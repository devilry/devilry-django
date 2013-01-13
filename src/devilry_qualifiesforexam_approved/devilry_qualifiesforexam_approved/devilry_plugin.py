from devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .post_statussave import save_subset_settings



def noop(*args):
    pass


qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.all',
    url = reverse_lazy('devilry_qualifiesforexam_approved_all'),
    title = _('Students must pass ALL assignments'),
    description = _('Choose this option if you require your students to get a passing grade on all their assignments to qualify for final exams.'),
    post_statussave=noop
)

qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.subset',
    url = reverse_lazy('devilry_qualifiesforexam_approved_subset'),
    title = _('Students must pass a set of assignments selected by you'),
    description = _('Choose this option if you require your students to get a passing grade on a subset of their assignments to qualify for final exams. You select the assignments on the next page.'),
    post_statussave = save_subset_settings
)