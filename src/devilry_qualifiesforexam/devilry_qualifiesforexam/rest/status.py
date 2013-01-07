from django.shortcuts import get_object_or_404
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.resources import FormResource
from djangorestframework.response import ErrorResponse
from djangorestframework.response import Response
from djangorestframework import status as statuscodes
from django import forms
from django.db import transaction

from devilry.apps.core.models import Period
from devilry_qualifiesforexam.models import Status
from devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.utils.restformfields import ListOfTypedField
from devilry.utils.restformat import serialize_user
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment



class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['period', 'status', 'message', 'plugin', 'pluginsettings']

    passing_relatedstudentids = ListOfTypedField(coerce=int)


class StatusResource(FormResource):
    form = StatusForm


class StatusView(View):
    """
    API for ``QualifiesForFinalExamPeriodStatus``, that lets users list and add statuses.
    Includes marking students as qualified/disqualified for final exams.

    # GET
    With no period specified, list the latest status for all active periods, including
    useful statistics for a UI listing.

    With a period specified, return a detailed description of the latest status on that period,
    including all students on the period.

    # POST
    Marks students as qualified or unqualfied for final exams. All related students are
    marked on each POST, and the input is simply a list of those that qualifies.

    ## Parameters

    - ``period``: The period ID (last part of the URL-path).
    - ``status``: The status.
    - ``message``: The status message.
    - ``plugin``: The plugin that was used to generate the results.
    - ``pluginsettings``: The plugin settings that was used to generate the results.
    - ``passing_relatedstudentids``: List of related students that qualifies for final exam.
    """
    permissions = (IsAuthenticated,)
    resource = StatusResource

    def _permissioncheck(self, period):
        if self.request.user.is_superuser:
            return
        if not Period.where_is_admin(self.request.user).filter(id=period.id).exists():
            raise ErrorResponse(status=statuscodes.HTTP_403_FORBIDDEN)

    def post(self, request, id=None):
        period = self.CONTENT['period']
        self._permissioncheck(period)
        with transaction.commit_on_success():
            status = Status(
                period = period,
                status = self.CONTENT['status'],
                message = self.CONTENT['message'],
                user = self.request.user,
                plugin = self.CONTENT['plugin'],
                pluginsettings = self.CONTENT['pluginsettings']
            )
            status.full_clean()
            status.save()
            passing_relatedstudentids = set(self.CONTENT['passing_relatedstudentids'])
            for relatedstudent in period.relatedstudent_set.all():
                qualifies = QualifiesForFinalExam(
                    relatedstudent = relatedstudent,
                    status = status,
                    qualifies = relatedstudent.id in passing_relatedstudentids
                )
                qualifies.full_clean()
                qualifies.save()
        return Response(201, '')


    def _create_passing_relatedstudentids_map(self, status):
        out = {}
        for qualifies in status.students.filter(qualifies=True):
            out[str(qualifies.relatedstudent.id)] = True
        return out

    def _serialize_status(self, status):
        return {
            'period': status.period.id,
            'status': status.status,
            'createtime': status.createtime,
            'message': status.message,
            'user': serialize_user(status.user),
            'plugin': status.plugin,
            'pluginsettings': status.pluginsettings,
            'passing_relatedstudentids_map': self._create_passing_relatedstudentids_map(status)
        }

    def _get_instance(self, id):
        period = get_object_or_404(Period, id=id)
        self._permissioncheck(period)

        statusQry = period.qualifiedforexams_status.order_by('-createtime').all()
        if len(statusQry) == 0:
            raise ErrorResponse(statuscodes.HTTP_404_NOT_FOUND,
                {'detail': 'The period has no statuses'})

        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        return {
            'id': period.id,
            'perioddata': grouper.serialize(),
            'statuses': [self._serialize_status(status) for status in statusQry]
        }

    def _get_list(self):
        return []

    def get(self, request, id=None):
        if id:
            return self._get_instance(id)
        else:
            return self._get_list()
