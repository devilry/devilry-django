from datetime import datetime

import django.dispatch
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import IntegrityError
from django.conf import settings

from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.response import ErrorResponse
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_student.rest.helpers import IsPublishedAndCandidate



#: Signal used to signal that a delivery has been successfully completed
successful_delivery_signal = django.dispatch.Signal(providing_args=["delivery"])


DEFAULT_DEADLINE_EXPIRED_MESSAGE = _('Your active deadline, {deadline} has expired, and the administrators of {assignment} have configured HARD deadlines. This means that you can not add more deliveries to this assignment before an administrator have extended your deadline.')
DEADLINE_EXPIRED_MESSAGE = getattr(settings, 'DEADLINE_EXPIRED_MESSAGE', DEFAULT_DEADLINE_EXPIRED_MESSAGE)


class AddDeliveryForm(forms.Form):
    delivery_id = forms.IntegerField(required=False)
    finish = forms.BooleanField(required=False)
    respond_with_html_contenttype = forms.BooleanField(required=False)
    respond_with_200_status_on_error = forms.BooleanField(required=False)


class AddDeliveryResource(FormResource):
    form = AddDeliveryForm

    def validate_request(self, data, files=None):
        if 'file_to_add' in data:
            del data['file_to_add']
        return super(AddDeliveryResource, self).validate_request(data, files)


class AddDeliveryView(View):
    """
    Makes it easy to add a delivery on a Group.

    **NOTE:** This is not strictly a REST API, however it is a programming API, developed using Djangorestframework.


    # POST
    To create a Delivery, you make one or more POST-requests. The content-type of the request
    should be ``multipart/form-data``.

    ## Parameters

    - ``file_to_add`` (not required): A file to add to the delivery. See the [w3 docs](http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2)
      for the format of file uploads in multiplart forms.
    - ``delivery_id``: The ID of a delivery to change. If this is ``null``, a new delivery is
      created. You will normally make one request to create a delivery, and include the
      ``delivery_id`` from the response of the first request in subsequent
      requests (to upload more files or finish the delivery).
    - ``finish`` (not required): Finish the delivery? If this is ``true``, we
      sets the ``successful`` flag if the delivery to ``True``, which makes is
      impossible to make further changes to the delivery.

    ## Response
    An object/map/dict with the following attributes:

    - ``group_id`` (int): The ID of the group (the same as the ID in the URL).
    - ``deadline_id`` (int): The ID of the deadline where the delivery is made.
    - ``delivery_id`` (int): The ID of the delivery.
    - ``added_filename`` (string|null): The name of the uploaded file, if
      ``file_to_add`` was supplied in the request.
    - ``created_delivery`` (bool): Did the request create a new delivery? Will
      always be ``true`` when ``delivery_id`` is omitted from the request.
    - ``finished`` (bool): Did the request finish the delivery? Will always be
      ``true`` if the ``finish=true``-parameter was in the request.
    - ``success`` (bool): ``true`` when the request is successful. This is only
      included to make integration with ExtJS easier. Status code is normally
      used for this purpose.
    """
    resource = AddDeliveryResource
    permissions = (IsAuthenticated, IsPublishedAndCandidate)

    def post(self, request, id):
        group_id = int(id)
        self.group = self._get_or_notfounderror(AssignmentGroup, group_id)

        if not self.group.is_open:
            self._raise_error_response(400, 'Can not add deliveries on closed groups.')

        if not self.group.is_open:
            self._raise_error_response(400, 'Can not add deliveries on closed groups.')

        self.deadline = self.group.get_active_deadline()
        self._validate_hard_deadlines()

        self.delivery, created_delivery = self._create_or_get_delivery()
        filename = None
        if 'file_to_add' in request.FILES:
            filename = self._add_file()

        finished = False
        if self.CONTENT['finish']:
            self._finish()
            finished = True

        result = {'group_id': group_id,
                  'deadline_id': self.deadline.id,
                  'delivery_id': self.delivery.id,
                  'added_filename': filename,
                  'created_delivery': created_delivery,
                  'finished': finished,
                  'success': True} # NOTE: ``success`` is included for ExtJS compatibility
        return result


    def _validate_hard_deadlines(self):
        assignment = self.deadline.assignment_group.parentnode
        if assignment.deadline_handling == Assignment.DEADLINEHANDLING_HARD:
            if self.deadline.deadline < datetime.now():
                self._raise_error_response(400,
                        DEADLINE_EXPIRED_MESSAGE.format(
                            deadline=self.deadline.deadline.isoformat(),
                            assignment=unicode(assignment)))

    def render(self, response):
        httpresponse = super(AddDeliveryView, self).render(response)
        if self.CONTENT['respond_with_html_contenttype']:
            httpresponse['content-type'] = 'text/html'
        return httpresponse

    def _get_or_notfounderror(self, modelcls, id):
        try:
            return modelcls.objects.get(id=id)
        except modelcls.DoesNotExist:
            self._raise_error_response(403, 'No {0} with ID={1}'.format(modelcls.__name__, id))

    def _finish(self):
        self.delivery.successful = True
        self.delivery.delivered_by = self._get_canidate()
        self.delivery.full_clean()
        self.delivery.save()
        successful_delivery_signal.send_robust(sender=self.delivery, delivery=self.delivery)

    def _get_canidate(self):
        try:
            return self.group.candidates.get(student=self.request.user)
        except Candidate.DoesNotExist:
            return None

    def _create_or_get_delivery(self):
        delivery_id = self.CONTENT['delivery_id']
        if delivery_id == None:
            return self._create_delivery(), True
        else:
            delivery = self._get_or_notfounderror(Delivery, delivery_id)
            if delivery.successful:
                raise self._raise_error_response(400, 'Can not change finished deliveries.')
            return delivery, False

    def _create_delivery(self):
        delivery = self.deadline.deliveries.create(successful=False,
                                                   delivered_by=self._get_canidate())
        return delivery

    def _add_file(self):
        file_to_add = self.request.FILES['file_to_add']
        filename = file_to_add.name

        try:
            self.delivery.add_file(filename, file_to_add.chunks())
        except IntegrityError, e:
            self._raise_error_response(400, _('Filename must be unique'))
        self.delivery.full_clean()
        self.delivery.save()
        return filename

    def _raise_error_response(self, statuscode, message):
        if self.CONTENT['respond_with_200_status_on_error']:
            statuscode = 200 # This is required for IE
        raise ErrorResponse(statuscode, {'detail': unicode(message),
                                         'success': False})
