#from django.utils.translation import ugettext as _
from django import forms
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.utils.passed_in_previous_period import MarkAsPassedInPreviousPeriod
from devilry.apps.core.models import Assignment
from devilry.apps.gradeeditors import gradeeditor_registry
from .errors import NotFoundError
from .auth import IsAssignmentAdmin
from .group import GroupSerializer
from .fields import DictField



class GroupField(DictField):
    class Form(forms.Form):
        id = forms.IntegerField(required=True)
        candidates = forms.CharField(required=False) # Ignored

class FeedbackField(DictField):
    class Form(forms.Form):
        grade = forms.CharField(required=True)
        points = forms.IntegerField(required=True)
        is_passing_grade = forms.BooleanField(required=False)
        rendered_view = forms.CharField(required=False)

class PassedInPreviousPeriodForm(forms.Form):
    id = forms.IntegerField(required=False) # Ignored - see node about ExtJS further down
    group = GroupField(required=True)
    feedback = FeedbackField(required=False)
    oldgroup = forms.CharField(required=False) # Ignored
    whyignored = forms.CharField(required=False) # Ignored


class PassedInPreviousPeriodResource(FormResource):
    form = PassedInPreviousPeriodForm
    fields = ('group', 'oldgroup', 'whyignored', 'feedback')



class ResultSerializer(object):
    def __init__(self, shortformat, result):
        self.shortformat = shortformat
        self.result = result

    def _serialize_basenode(self, basenode):
        return {'id': basenode.id,
                'short_name': basenode.short_name,
                'long_name': basenode.long_name}

    def _serialize_group(self, group):
        groupserializer = GroupSerializer(group)
        return {'id': group.id,
                'name': group.name,
                'candidates': groupserializer.serialize_candidates()}

    def _serialize_oldgroup(self, oldgroup):
        assignment = oldgroup.parentnode
        period = assignment.parentnode
        return {'id': oldgroup.id,
                'shortformat_widget': self.shortformat.widget,
                'oldfeedback_shortformat': self.shortformat.format_feedback(oldgroup.feedback),
                'assignment': self._serialize_basenode(assignment),
                'period': self._serialize_basenode(period)}

    def _serialize_marked(self):
        for group, oldgroup in self.result['marked']:
            self._add(group, oldgroup=oldgroup)

    def _serialize_ignored(self):
        for whyignored, ignoredgroups in self.result['ignored'].iteritems():
            for group in ignoredgroups:
                self._add(group, whyignored=whyignored)

    def _add(self, group, oldgroup=None, whyignored=None):
        if oldgroup != None:
            oldgroup = self._serialize_oldgroup(oldgroup)
        self.serialized.append({'id': group.id, # Included because ExtJS requires an id-property, and group.id does not work - does not hinder other clients in any way, and the overhead is minimal.
                                'group': self._serialize_group(group),
                                'oldgroup': oldgroup,
                                'whyignored': whyignored})

    def serialize(self):
        self.serialized = []
        self._serialize_ignored()
        self._serialize_marked()
        return self.serialized


class PassedInPreviousPeriod(View):
    """
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = PassedInPreviousPeriodResource

    def validate_request(self, datalist, files=None):
        cleaned_datalist = []
        for data in datalist:
            cleaned_data = super(PassedInPreviousPeriod, self).validate_request(data)
            cleaned_datalist.append(cleaned_data)
        return cleaned_datalist

    def _get_assignment(self, id):
        try:
            return Assignment.objects.get(id=id)
        except Assignment.DoesNotExist:
            raise NotFoundError('Assignment with id={0} not found'.format(id))

    def _get_shortformat(self):
        gradeeditorid = self.assignment.gradeeditor_config.gradeeditorid
        shortformat = gradeeditor_registry[gradeeditorid].shortformat
        if shortformat:
            return shortformat
        else:
            raise ErrorResponse(status.HTTP_400_BAD_REQUEST, {
                'detail': 'The grading system, {gradingsystem}, does not support shortformat, which is requried by this API.'.format(gradingsystem=gradeeditorid)
            })

    def get(self, request, id):
        self.assignment = self._get_assignment(id)
        return self._get_result()

    def _get_result(self):
        marker = MarkAsPassedInPreviousPeriod(self.assignment)
        result = marker.mark_all(pretend=True)
        return ResultSerializer(self._get_shortformat(), result).serialize()

    def put(self, request, id):
        self.assignment = self._get_assignment(id)
        marker = MarkAsPassedInPreviousPeriod(self.assignment)
        group_ids = [item['group']['id'] for item in self.CONTENT]
        for item in self.CONTENT:
            group = self.assignment.assignmentgroups.get(id=item['group']['id'])
            feedback = item['feedback']
            if feedback:
                feedback['saved_by'] = self.request.user # NOTE: If we do not get a feedback, a search for old feedbacks is performed, and saved_by is copied from the old feedback.
            marker.mark_group(group, feedback=feedback)
        return self._get_result()
