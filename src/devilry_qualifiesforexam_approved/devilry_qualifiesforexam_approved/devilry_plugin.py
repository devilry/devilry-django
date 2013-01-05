from devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _


qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.all',
    url = reverse_lazy('devilry_qualifiesforexam_approved_all'),
    title = _('Students must pass ALL assignments'),
    description = _('Choose this option if you require your students to get a passing grade on all their assignments to qualify for final exams.')
)

qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.subset',
    url = '', #reverse('myapp-myplugin'), # The url of the view to use for step/page 2 in the workflow
    title = _('Students must pass a set of assignments selected by you'),
    description = _('Choose this option if you require your students to get a passing grade on a subset of their assignments to qualify for final exams. You select the assignments on the next page.')
)