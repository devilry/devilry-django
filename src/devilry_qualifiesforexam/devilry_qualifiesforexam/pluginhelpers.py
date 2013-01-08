from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from devilry.apps.core.models import Period


def create_sessionkey(pluginsessionid):
    return 'qualifiesforexam-{0}'.format(pluginsessionid)


class PreviewData(object):
    def __init__(self, passing_relatedstudentids):
        self.passing_relatedstudentids = passing_relatedstudentids

    def __str__(self):
        return '{0!r}'.format(self.passing_relatedstudentids)

    def serialize(self):
        return {
            'passing_relatedstudentids': self.passing_relatedstudentids
        }

class QualifiesForExamViewMixin(object):
    def get_plugin_input_and_authenticate(self):
        self.periodid = self.request.GET['periodid']
        if not Period.where_is_admin_or_superadmin(self.request.user).filter(id=self.periodid).exists():
            raise PermissionDenied()
        self.period = get_object_or_404(Period, pk=self.periodid)
        self.pluginsessionid = self.request.GET['pluginsessionid']

    def save_plugin_output(self, *args, **kwargs):
        self.request.session[create_sessionkey(self.pluginsessionid)] = PreviewData(*args, **kwargs)

    def get_preview_url(self):
        return '{url}?routeto=/{periodid}/preview/{pluginsessionid}'.format(
            url=reverse('devilry_qualifiesforexam_ui'),
            periodid = self.periodid,
            pluginsessionid = self.pluginsessionid)
