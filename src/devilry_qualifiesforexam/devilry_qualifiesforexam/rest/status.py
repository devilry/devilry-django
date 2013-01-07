from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.resources import FormResource
from djangorestframework.response import ErrorResponse
from djangorestframework.response import Response
from djangorestframework import status
from django import forms
from django.db import transaction

from devilry.apps.core.models import Period
from devilry_qualifiesforexam.models import Status
from devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.utils.restformfields import ListOfTypedField





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
            raise ErrorResponse(status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
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

    def get(self, request):
        return ['hei']