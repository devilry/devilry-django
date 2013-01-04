from devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.all',
    url = '', #reverse('myapp-myplugin'), # The url of the view to use for step/page 2 in the workflow
    title = _('Approved grade on ALL assignments'),
    description = _('Choose this option if you require your students to pass all the assignments.')
)

qualifiesforexam_plugins.add(
    id = 'devilry_qualifiesforexam_approved.subset',
    url = '', #reverse('myapp-myplugin'), # The url of the view to use for step/page 2 in the workflow
    title = _('Approved grade on some assignments'),
    description = _('Choose this option if you require your students to pass some of the assignments.')
)