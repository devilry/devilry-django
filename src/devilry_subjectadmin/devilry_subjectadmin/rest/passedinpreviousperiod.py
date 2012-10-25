#from django.utils.translation import ugettext as _
from django import forms
#from django.db import transaction
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.permissions import IsAuthenticated
#from djangorestframework.response import Response

from devilry.utils.passed_in_previous_period import MarkAsPassedInPreviousPeriod
from devilry.apps.core.models import Assignment
#from .errors import PermissionDeniedError
from .errors import NotFoundError
from .auth import IsAssignmentAdmin
from .group import GroupSerializer
#from .log import logger



class PassedInPreviousPeriodForm(forms.Form):
    deadline = forms.DateTimeField(required=True)


class PassedInPreviousPeriodResource(FormResource):
    form = PassedInPreviousPeriodForm



class ResultSerializer(object):
    def __init__(self, result):
        self.result = result

    def _serialize_basenode(self, basenode):
        return {'id': basenode.id,
                'short_name': basenode.short_name,
                'long_name': basenode.long_name}

    def _serialize_group(self, group):
        groupserializer = GroupSerializer(group)
        return {'id': group.id,
                'candidates': groupserializer.serialize_candidates()}

    def _serialize_oldgroup(self, oldgroup):
        assignment = oldgroup.parentnode
        period = assignment.parentnode
        return {'id': oldgroup.id,
                'assignment': self._serialize_basenode(assignment),
                'period': self._serialize_basenode(period)}

    def _serialize_group_oldgroup_tuple(self, groups):
        group, oldgroup = groups
        return {'group': self._serialize_group(group),
                'oldgroup': self._serialize_oldgroup(oldgroup)}

    def _serialize_marked(self):
        return map(self._serialize_group_oldgroup_tuple, self.result['marked'])


    def _serialize_ignored(self):
        ignored = {}
        has_ignored = False
        for key, ignoredgroups in self.result['ignored'].iteritems():
            if len(ignoredgroups) > 0:
                has_ignored = True
            ignored[key] = map(self._serialize_group, ignoredgroups)
        return ignored, has_ignored

    def serialize(self):
        ignored, has_ignored = self._serialize_ignored()
        return {'passed_in_previous_period': self._serialize_marked(),
                'ignored': ignored,
                'has_ignored': has_ignored}


class PassedInPreviousPeriod(View):
    """
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = PassedInPreviousPeriodResource

    def _get_assignment(self, id):
        try:
            return Assignment.objects.get(id=id)
        except Assignment.DoesNotExist:
            raise NotFoundError('Assignment with id={0} not found'.format(id))

    def get(self, request, id):
        assignment = self._get_assignment(id)
        marker = MarkAsPassedInPreviousPeriod(assignment)
        result = marker.mark_all(pretend=True)
        return ResultSerializer(result).serialize()
