from django.shortcuts import get_object_or_404

from devilry.apps.core.models import Period


# TODO: Auth


def create_sessionkey(pluginsessionid):
    return 'qualifiesforexam-{0}'.format(pluginsessionid)


class PreviewData(object):
    def __init__(self, passing_relatedstudentids):
        self.passing_relatedstudentids = passing_relatedstudentids


class QualifiesForExamViewMixin(object):
    def get_plugin_input(self):
        self.periodid = self.request.GET['periodid']
        self.period = get_object_or_404(Period, pk=self.periodid)
        self.pluginsessionid = self.request.GET['pluginsessionid']

    def save_plugin_output(self, *args, **kwargs):
        self.request.session[create_sessionkey(self.pluginsessionid)] = PreviewData(*args, **kwargs)
