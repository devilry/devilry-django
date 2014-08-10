#from django.utils.translation import ugettext as _
from django import forms
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status
from django.db import transaction

from devilry.utils.passed_in_previous_period import MarkAsPassedInPreviousPeriod
from devilry.utils.passed_in_previous_period import MarkAsPassedInPreviousPeriodError
from devilry.apps.core.models import Assignment
# from devilry.apps.gradeeditors import gradeeditor_registry
# from devilry.apps.gradeeditors import ShortFormatValidationError
from .errors import NotFoundError
from .errors import BadRequestFieldError
from .errors import ValidationErrorResponse
from .auth import IsAssignmentAdmin
from .group import GroupSerializer


# TODO: Update to work with gradingsystem plugins



class PassedInPreviousPeriodForm(forms.Form):
    id = forms.IntegerField(required=True)
    newfeedback_shortformat = forms.CharField(required=True)


class PassedInPreviousPeriodResource(FormResource):
    form = PassedInPreviousPeriodForm



class ResultSerializer(object):
    def __init__(self, gradeeditor_config, shortformat, result):
        self.gradeeditor_config = gradeeditor_config
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
                'feedback_shortformat': self.shortformat.format_feedback(
                    self.gradeeditor_config, oldgroup.feedback),
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
    Autodetect and mark groups as passed previous periods.

    # Parameters
    Takes the ``id`` of the assignment as the last segment of the url PATH.

    # GET

    ## Returns
    Returns a list/array where each item is an object describing a group on the current assignment
    with the following attributes:

    - ``id``: The ID of the group (same as the id-attribute of the ``group`` below).
    - ``group``: An object with details about the group. Has the following attributes:
        - ``candidates``: A list of candidates on the group. Each candidate has the following
          attributes:
            - ``id``: The ID of the candidate object.
            - ``candidate_id``: The candidateID for this candidate - used on anonymous assignments.
            - ``user``: An object describing the user with the following attributes:
                - ``id``: The internal ID for the user.
                - ``displayname``: The name of the user if available, otherwise, the username.
                - ``username``: The username.
                - ``full_name``: The full name of the user, or ``null``.
                - ``email``: The email-address of the user.
    - ``oldgroup``: An object describing an autodetected old group with passing grade and the same
        candidates as this group. ``null`` if no such group is detected. Has the following attributes:
            - ``id``: The ID of the old group.
            - ``assignment``: An object describing the assignment of the old group. Attributes:
                ``id``: ID of the assignment.
                ``short_name``: Short name of the assignment.
                ``long_name``: Long name of the assignment.
            - ``period``: An object describing the period of the old group. Attributes:
                ``id``: ID of the period.
                ``short_name``: Short name of the period.
                ``long_name``: Long name of the period.
            - ``feedback_shortformat``: The shortformat formatted feedback of the old group.

    # PUT
    Mark groups as passed previously. Takes a list/array of groups to pass, each group is an object
    with the following attributes:

    - ``id`` (int): The ID of a group that should be marked as approved in a previous period.
      Must be a group in the
    - ``newfeedback_shortformat`` (string|null): The feedback that should be added to the delivery
      that is made to mark this as a previously passed group. If this is ``null``, we try to
      autodetect the feedback, and autolink the feedback with an old feedback. You should
      generally only set this to ``null`` if GET returns ``oldgroup!=null`` for the group.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = PassedInPreviousPeriodResource

    def validate_request(self, datalist, files=None):
        cleaned_datalist = []
        if not isinstance(datalist, list):
            datalist = [datalist]
        for data in datalist:
            cleaned_data = super(PassedInPreviousPeriod, self).validate_request(data)
            cleaned_datalist.append(cleaned_data)
        return cleaned_datalist

    def _get_assignment(self, id):
        try:
            return Assignment.objects.get(id=id)
        except Assignment.DoesNotExist:
            raise NotFoundError('Assignment with id={0} not found'.format(id))

    def _get_gradeeditor_config_and_shortformat(self):
        gradeeditor_config = self.assignment.gradeeditor_config
        shortformat = gradeeditor_registry[gradeeditor_config.gradeeditorid].shortformat
        if shortformat:
            return gradeeditor_config, shortformat
        else:
            raise ErrorResponse(status.HTTP_400_BAD_REQUEST, {
                'detail': 'The grading system, {gradingsystem}, does not support shortformat, which is requried by this API.'.format(gradingsystem=gradeeditor_config.gradeeditorid)
            })

    def get(self, request, id):
        self.assignment = self._get_assignment(id)
        return self._get_result()

    def _get_result(self):
        marker = MarkAsPassedInPreviousPeriod(self.assignment)
        result = marker.mark_all(pretend=True)
        gradeeditor_config, shortformat = self._get_gradeeditor_config_and_shortformat()
        return ResultSerializer(gradeeditor_config, shortformat, result).serialize()

    def put(self, request, id):
        self.assignment = self._get_assignment(id)
        marker = MarkAsPassedInPreviousPeriod(self.assignment)
        gradeeditor_config, shortformat = self._get_gradeeditor_config_and_shortformat()
        with transaction.commit_on_success():
            for item in self.CONTENT:
                group = self.assignment.assignmentgroups.get(id=item['id'])
                newfeedback_shortformat = item['newfeedback_shortformat']
                try:
                    shortformat.validate(gradeeditor_config, newfeedback_shortformat)
                except ShortFormatValidationError as e:
                    raise ValidationErrorResponse(e)
                feedback = shortformat.to_staticfeedback_kwargs(gradeeditor_config, newfeedback_shortformat)
                if not feedback['is_passing_grade']:
                    raise BadRequestFieldError('newfeedback_shortformat', 'Must be a passing grade')
                feedback['rendered_view'] = ''
                feedback['saved_by'] = self.request.user

                oldgroup = None
                try:
                    oldgroup = marker.find_previously_passed_group(group)
                except MarkAsPassedInPreviousPeriodError:
                    pass
                created_feedback = marker.mark_as_delivered_in_previous(group, oldgroup=oldgroup,
                        feedback=feedback)
        return self._get_result()
