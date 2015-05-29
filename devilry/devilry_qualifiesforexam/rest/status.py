from django.shortcuts import get_object_or_404
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.resources import FormResource
from djangorestframework.response import ErrorResponse
from djangorestframework.response import Response
from djangorestframework import status as statuscodes
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError

from devilry.apps.core.models import Period
from devilry.devilry_qualifiesforexam.models import Status
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.devilry_rest.formfields import ListOfTypedField
from devilry.devilry_rest.serializehelpers import serialize_user
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment
from devilry.devilry_qualifiesforexam.registry import qualifiesforexam_plugins
from devilry.devilry_qualifiesforexam.pluginhelpers import create_settings_sessionkey
from devilry.devilry_qualifiesforexam.pluginhelpers import PluginResultsFailedVerification


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['period', 'status', 'message', 'plugin']

    passing_relatedstudentids = ListOfTypedField(coerce=int, required=False)
    notready_relatedstudentids = ListOfTypedField(coerce=int, required=False)
    pluginsessionid = forms.CharField(required=False)


class StatusResource(FormResource):
    form = StatusForm


# def validate_request(self, data, files=None):
#        if data['notready_relatedstudentids'] and data['status'] != 'almostready':
#            return
#        return super(StatusResource, self).validate_request(data, files)



class StatusView(View):
    """
    API for ``QualifiesForFinalExamPeriodStatus``, that lets users list and add statuses.
    Includes marking students as qualified/disqualified for final exams.


    # GET

    ## With no period specified
    With no period specified (URL ends in ``/``), list the latest status for
    all active periods, including useful statistics for a UI listing.


    ### Parameters - given via the querystring
    
    - ``node_id`` (optional): Limit to periods within a given ``node_id``.

    ### Response
    A list where each object has the following attributes:

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
            - ``pluginsettings_summary``: Human-readable summary of the settings used to generate the status.


    ## With period specified

    With a period specified (last part of URL), return a detailed description
    of the latest status on that period, including all students on the period.
    The object has the same attributes as the items in the listing described
    above, but with some new and remove attributes:

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
    - ``status``: The status. One of:
        - ``notready``: Retracted from one of the other statuses - not ready for export. Students
          are ignored, only a message is stored.
        - ``ready``: Ready for export.
        - ``almostready``: Almost ready for export. Student that are not ready are in the ``notready_relatedstudentids``-parameter.
    - ``message``: The status message. Can not be empty when the status is ``notready``.
    - ``plugin``: The plugin that was used to generate the results. Must be ``null`` when status is ``notready``, and required for all other statuses.
    - ``passing_relatedstudentids``: List of related students that qualifies for final exam.
    - ``notready_relatedstudentids``: List of related students that are not ready to be exported.
      These are stored with the value ``None`` (``NULL``) in the ``qualifies`` database field.
      For all statuses except ``almostready``, it is an error if this is not empty or ``null``.
    """
    permissions = (IsAuthenticated,)
    resource = StatusResource

    def _permissioncheck(self, period):
        if self.request.user.is_superuser:
            return
        if not Period.where_is_admin(self.request.user).filter(id=period.id).exists():
            raise ErrorResponse(status=statuscodes.HTTP_403_FORBIDDEN)

    def _invoke_post_statussave(self, status):
        pluginsessionid = self.CONTENT['pluginsessionid']
        settings = None
        if qualifiesforexam_plugins.uses_settings(status.plugin):
            try:
                settings = self.request.session.pop(create_settings_sessionkey(pluginsessionid))
            except KeyError:
                msg = 'The "{0}"-plugin requires settings - no settings found in the session.'.format(status.plugin)
                raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST, {'detail': msg})
        try:
            qualifiesforexam_plugins.post_statussave(status, settings)
        except PluginResultsFailedVerification as e:
            raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST, {'detail': str(e)})

    def post(self, request, id=None):
        period = self.CONTENT['period']
        self._permissioncheck(period)
        with transaction.commit_on_success():
            status = Status(
                period=period,
                status=self.CONTENT['status'],
                message=self.CONTENT['message'],
                user=self.request.user,
                plugin=self.CONTENT['plugin']
            )
            status.full_clean()
            status.save()
            if status.status != 'notready':
                passing_relatedstudentids = set(self.CONTENT['passing_relatedstudentids'])
                notready_relatedstudentids = set(self.CONTENT['notready_relatedstudentids'])
                for relatedstudent in period.relatedstudent_set.all():
                    if relatedstudent.id in notready_relatedstudentids:
                        qualifies = None
                    else:
                        qualifies = relatedstudent.id in passing_relatedstudentids
                    qualifies = QualifiesForFinalExam(
                        relatedstudent=relatedstudent,
                        status=status,
                        qualifies=qualifies
                    )
                    try:
                        qualifies.full_clean()
                    except ValidationError as e:
                        raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST,
                                            {'details': ' '.join(e.messages)})
                    qualifies.save()
                if status.plugin and qualifiesforexam_plugins.has_post_statussave(status):
                    self._invoke_post_statussave(status)
        return Response(201, '')

    def _create_passing_relatedstudentids_map(self, status):
        out = {}
        for qualifies in status.students.filter(qualifies=True):
            out[str(qualifies.relatedstudent_id)] = True
        return out

    def _serialize_status(self, status, includedetails=True):
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
            'plugin': status.plugin
        }
        if status.plugin:
            out['plugin_title'] = unicode(qualifiesforexam_plugins.get_title(status.plugin))
        if includedetails:
            out['passing_relatedstudentids_map'] = self._create_passing_relatedstudentids_map(status)
            if status.plugin:
                out['pluginsettings_summary'] = qualifiesforexam_plugins.get_pluginsettings_summary(status)
                out['plugin_description'] = unicode(qualifiesforexam_plugins.get_description(status.plugin))
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
        if statusQry.count() == 0:
            raise ErrorResponse(statuscodes.HTTP_404_NOT_FOUND,
                                {'detail': 'The period has no statuses'})
        statusQry = statusQry.select_related(
            'period', 'user', 'user__devilryuserprofile')

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
        out.update({'active_status': self._serialize_status(active_status, includedetails=False)})
        return out

    def _get_list(self):
        qry = Period.where_is_admin_or_superadmin(self.request.user)
        qry = qry.filter(Period.q_is_active())
        if self.request.GET.get('node_id', None) != None:
            qry = qry.filter(parentnode__parentnode=self.request.GET['node_id'])
        qry = qry.prefetch_related('qualifiedforexams_status')
        qry = qry.select_related('parentnode')
        qry = qry.order_by('parentnode__long_name', 'start_time')
        return [self._listserialize_period(period) for period in qry]

    def get(self, request, id=None):
        if id:
            return self._get_instance(id)
        else:
            return self._get_list()
