from datetime import datetime
import uuid
from django.contrib import messages
from django.db import IntegrityError
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django_cradmin import crapp
from devilry.apps.core.models import Assignment, Candidate, Delivery


DEFAULT_DEADLINE_EXPIRED_MESSAGE = _('Your active deadline, {deadline} has expired, and the administrators of {assignment} have configured HARD deadlines. This means that you can not add more deliveries to this assignment before an administrator have extended your deadline.')
DEADLINE_EXPIRED_MESSAGE = getattr(settings, 'DEADLINE_EXPIRED_MESSAGE', DEFAULT_DEADLINE_EXPIRED_MESSAGE)


class FileMetaForm(forms.Form):
    file = forms.FileField(
        label=_('Upload a file'))


class AddDeliveryView(TemplateView):
    template_name = 'devilry_student/cradmin_group/add_delivery.django.html'

    def _fatal_error_response(self, message):
        messages.error(self.request, message)
        return HttpResponseRedirect(self.request.cradmin_instance.rolefrontpage_url(self.group.id))

    def __init__(self, *args, **kwargs):
        self.group = None
        self.deadline_has_expired = None
        self.active_deadline = None
        super(AddDeliveryView, self).__init__(*args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        self.group = self.request.cradmin_role
        if not self.group.is_open:
            return self.render_to_response(self.get_context_data())

        self.active_deadline = self.group.get_active_deadline()
        if self.active_deadline is None:
            return self.render_to_response(self.get_context_data())

        self.deadline_has_expired = self._deadline_has_expired(self.active_deadline)
        if self.deadline_has_expired == 'hard':
            return self.render_to_response(self.get_context_data(deadline_has_expired=True))

        return super(AddDeliveryView, self).dispatch(request, *args, **kwargs)

    def _deadline_has_expired(self, deadline):
        assignment = self.group.parentnode
        if deadline.deadline < datetime.now():
            if assignment.deadline_handling == Assignment.DEADLINEHANDLING_HARD:
                return 'hard'
            else:
                return 'soft'
        else:
            return False

    def post(self, *args, **kwargs):
        FileMetaFormSet = formset_factory(FileMetaForm)
        filemetaformset = FileMetaFormSet(self.request.POST, self.request.FILES)
        if filemetaformset.is_valid():
            return self.form_valid(filemetaformset)
        else:
            raise Exception('Getting here should not be possible.')

    def __get_canidate(self):
        try:
            return self.group.candidates.get(student=self.request.user)
        except Candidate.DoesNotExist:
            return None

    def get_success_url(self, delivery):
        return self.request.cradmin_instance.reverse_url('deliveries', 'deliverydetails', kwargs={
            'pk': delivery.pk})

    def __create_delivery(self):
        delivery = Delivery(
            deadline=self.active_deadline,
            successful=True,
            delivered_by=self.__get_canidate(),
            time_of_delivery=datetime.now())
        delivery.set_number()
        delivery.full_clean()
        delivery.save()
        return delivery

    def __create_filemeta(self, delivery, uploadedfile, filename):
        try:
            delivery.add_file(filename, uploadedfile.chunks())
        except IntegrityError:
            filename = u'{}-{}'.format(str(uuid.uuid4()), filename)
            self.__create_filemeta(delivery, uploadedfile, filename)

    def form_valid(self, filemetaformset):
        delivery = self.__create_delivery()
        for data in filemetaformset.cleaned_data:
            uploadedfile = data['file']
            self.__create_filemeta(
                delivery=delivery,
                uploadedfile=uploadedfile,
                filename=uploadedfile.name)
        self.group.last_delivery = delivery
        self.group.save(update_delivery_status=False)
        return HttpResponseRedirect(self.get_success_url(delivery))

    def get_context_data(self, **kwargs):
        context = super(AddDeliveryView, self).get_context_data(**kwargs)
        FileMetaFormSet = formset_factory(FileMetaForm, extra=1)
        filemetaformset = FileMetaFormSet()
        context['filemetaformset'] = filemetaformset
        context['deadline_has_expired'] = self.deadline_has_expired
        context['active_deadline'] = self.active_deadline
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', AddDeliveryView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
