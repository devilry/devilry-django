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
    useful statistics for a UI listing. For each item in the listing, we yield and object
    with the following attributes:

    - ``id``: The period id.
    - ``is_active``: Is the period active? (boolean)
    - ``short_name``: The short name of the period.
    - ``long_name``: The long name of the period.
    - ``subject``: An object describing the subject (attributed: ``id``, ``short_name``, ``long_name``).
    - ``active_status``: An object describing the active status, or ``null``. The object
      has the following attributes:
           - ``id``: The ID of the status.
            - ``period``: The ID of the period.
            - ``status``: Short identifier for the status.
            - ``createtime``: The creation time of the status.
            - ``message``: A message for this status (added by the one that saved it).
            - ``user``: An object with information about the user that saved the status. Attributes:
               ``id``, ``username``, ``full_name``, ``email``.
            - ``plugin``: The ID of the plugin used to generate the list of qualified students.
            - ``pluginsettings``: Settings provided to the plugin to geneate the list of qualified students.

    With a period specified, return a detailed description of the latest status on that period,
    including all students on the period. The object has the same attributes as the items in
    the listing described above, but with some new and remove attributes:

    - ``perioddata``: Contains detailed data for all students in the period.
    - ``statuses``: Instead of ``active_status``, we return a list of all statuses,
      where the active status is the first item. Each status in the list includes
      an additional attribute, ``passing_relatedstudentids_map``, which contains
      a map with the ID of all the relatedstudents with passing grade.

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

    def _serialize_status(self, status, includestudents=True):
        if not status:
            return None
        out = {
            'id': status.id,
            'period': status.period.id,
            'status': status.status,
            'statustext': unicode(status.getStatusText()),
            'createtime': status.createtime,
            'message': status.message,
            'user': serialize_user(status.user),
            'plugin': status.plugin,
            'pluginsettings': status.pluginsettings,
        }
        if includestudents:
            out['passing_relatedstudentids_map'] = self._create_passing_relatedstudentids_map(status)
        return out

    def _serialize_period(self, period):
        return {
            'id': period.id,
            'short_name': period.short_name,
            'long_name': period.long_name,
            'is_active': period.is_active(),
            'subject': {
                'id': period.parentnode.id,
                'short_name': period.parentnode.short_name,
                'long_name': period.parentnode.long_name
            }
        }

    def _get_instance(self, id):
        try:
            qry = Period.objects.select_related('parentnode')
            period = qry.get(id=id)
        except Period.DoesNotExist:
            raise ErrorResponse(statuscodes.HTTP_404_NOT_FOUND,
                {'detail': 'The period with ID {id} does not exist'.format(id=id)})

        self._permissioncheck(period)

        statusQry = period.qualifiedforexams_status.all()
        if len(statusQry) == 0:
            raise ErrorResponse(statuscodes.HTTP_404_NOT_FOUND,
                {'detail': 'The period has no statuses'})

        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        out = self._serialize_period(period)
        out.update({
            'perioddata': grouper.serialize(),
            'statuses': [self._serialize_status(status) for status in statusQry]
        })
        return out

    def _listserialize_period(self, period):
        statuses = period.qualifiedforexams_status.all()[:1]
        if len(statuses) == 0:
            active_status = None
        else:
            active_status = statuses[0]
        out = self._serialize_period(period)
        out.update({'active_status': self._serialize_status(active_status, includestudents=False)})
        return out

    def _get_list(self):
        qry = Period.where_is_admin_or_superadmin(self.request.user)
        qry = qry.filter(Period.q_is_active())
        qry = qry.prefetch_related('qualifiedforexams_status')
        qry = qry.select_related('parentnode')
        qry = qry.order_by('start_time')
        return [self._listserialize_period(period) for period in qry]

    def get(self, request, id=None):
        if id:
            return self._get_instance(id)
        else:
            return self._get_list()
