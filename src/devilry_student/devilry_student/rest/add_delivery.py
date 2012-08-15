from django.utils.translation import ugettext as _
from django import forms
from django.db import IntegrityError
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status
from djangorestframework.views import View
from djangorestframework.resources import FormResource

from devilry.apps.core.models import Delivery
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import AssignmentGroup
from .aggregated_groupinfo import IsCandidate


class NotFoundError(ErrorResponse):
    """
    Raised to signal that an item was not found
    """
    def __init__(self, errormsg):
        super(NotFoundError, self).__init__(status.HTTP_404_NOT_FOUND,
                                            {'detail': errormsg})

class BadRequestError(ErrorResponse):
    def __init__(self, errormsg):
        super(BadRequestError, self).__init__(status.HTTP_400_BAD_REQUEST,
                                              {'detail': errormsg})


class AddDeliveryForm(forms.Form):
    delivery_id = forms.IntegerField(required=False)
    finish = forms.BooleanField(required=False)


class AddDeliveryResource(FormResource):
    form = AddDeliveryForm


class AddDeliveryView(View):
    """
    Makes it easy to add a delivery on a Group.

    **NOTE:** This is not strictly a REST API, however it is a programming API, developed using Djangorestframework.


    # POST
    To create a Delivery, you make one or more POST-requests.
    """
    resource = AddDeliveryResource
    permissions = (IsAuthenticated, IsCandidate)

    def post(self, request, id):
        group_id = int(id)
        self.group = self._get_or_notfounderror(AssignmentGroup, group_id)

        if not self.group.is_open:
            raise BadRequestError('Can not add deliveries on closed groups.')

        self.deadline = self.group.get_active_deadline()
        self.delivery, created_delivery = self._create_or_get_delivery()

        filename = None
        if 'file_to_add' in request.FILES:
            filename = self._add_file()

        finished = False
        if self.CONTENT['finish']:
            self._finish()
            finished = True

        return {'group_id': group_id,
                'deadline_id': self.deadline.id,
                'delivery_id': self.delivery.id,
                'added_filename': filename,
                'created_delivery': created_delivery,
                'finished': finished}

    def _get_or_notfounderror(self, modelcls, id):
        try:
            return modelcls.objects.get(id=id)
        except modelcls.DoesNotExist, e:
            raise NotFoundError('No {0} with ID={1}'.format(modelcls.__name__, id))

    def _finish(self):
        self.delivery.successful = True
        self.delivery.save()

    def _create_or_get_delivery(self):
        delivery_id = self.CONTENT['delivery_id']
        if delivery_id == None:
            return self._create_delivery(), True
        else:
            delivery = self._get_or_notfounderror(Delivery, delivery_id)
            if delivery.successful:
                raise BadRequestError('Can not change finished deliveries.')
            return delivery, False

    def _create_delivery(self):
        delivery = self.deadline.deliveries.create(successful=False)
        return delivery

    def _add_file(self):
        file_to_add = self.request.FILES['file_to_add']
        filename = file_to_add.name

        try:
            self.delivery.add_file(filename, file_to_add.chunks())
        except IntegrityError, e:
            raise BadRequestError(_('Filename must be unique'))
        self.delivery.full_clean()
        self.delivery.save()
        return filename
