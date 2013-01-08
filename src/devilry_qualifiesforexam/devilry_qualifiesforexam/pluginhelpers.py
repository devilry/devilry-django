from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from crispy_forms.layout import Submit, HTML
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import Period


def create_sessionkey(pluginsessionid):
    return 'qualifiesforexam-{0}'.format(pluginsessionid)


class PreviewData(object):
    def __init__(self, passing_relatedstudentids):
        self.passing_relatedstudentids = passing_relatedstudentids

    def __str__(self):
        return 'PreviewData(passing_relatedstudentids={0!r})'.format(self.passing_relatedstudentids)

    def serialize(self):
        return {
            'passing_relatedstudentids': self.passing_relatedstudentids
        }

class QualifiesForExamPluginViewMixin(object):
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

    def get_selectplugin_url(self):
        return '{url}?routeto=/{periodid}/selectplugin'.format(
            url=reverse('devilry_qualifiesforexam_ui'),
            periodid = self.periodid)

    def redirect_to_preview_url(self):
        return HttpResponseRedirect(self.get_preview_url())

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        raise NotImplementedError()

    def get_relatedstudents_that_qualify_for_exam(self):
        passing_relatedstudentsids = []
        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.period)
        for aggregated_relstudentinfo in grouper.iter_relatedstudents_with_results():
            if self.student_qualifies_for_exam(aggregated_relstudentinfo):
                passing_relatedstudentsids.append(aggregated_relstudentinfo.relatedstudent.id)
        return passing_relatedstudentsids

    def handle_save_results_and_redirect_to_preview_request(self):
        try:
            self.get_plugin_input_and_authenticate() # set self.periodid and self.pluginsessionid
        except PermissionDenied:
            return HttpResponseForbidden()
        self.save_plugin_output(self.get_relatedstudents_that_qualify_for_exam())
        return self.redirect_to_preview_url()


class NextButton(Submit):
    field_classes = 'btn btn-primary btn-large'

    def __init__(self):
        super(NextButton, self).__init__('submit', _('Next'))

class BackButton(HTML):
    field_classes = 'btn btn-large'

    def __init__(self, backurl):
        html = '<a href="{url}" class="btn btn-large" style="margin-right: 5px;">{label}</a>'.format(
            url = backurl,
            label = unicode(_('Back'))
        )
        super(BackButton, self).__init__(html)
