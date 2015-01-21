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


class AddDeliveryForm(forms.Form):
    confirm_delivery_after_soft_deadline = forms.BooleanField(required=False)


class AddDeliveryView(TemplateView):
    template_name = 'devilry_student/cradmin_group/add_delivery.django.html'

    def _fatal_error_response(self, message):
        messages.error(self.request, message)
        return HttpResponseRedirect(self.request.cradmin_instance.rolefrontpage_url(self.group.id))

    def __init__(self, *args, **kwargs):
        self.group = None
        self.deadline_has_expired = None
        super(AddDeliveryView, self).__init__(*args, **kwargs)

    def __redirect_to_overview(self):
        return HttpResponseRedirect(self.request.cradmin_instance.appindex_url('deliveries'))

    def dispatch(self, request, *args, **kwargs):
        self.group = self.request.cradmin_role
        if not self.group.is_open:
            return self.__redirect_to_overview()

        if self.group.last_deadline_id is None:
            return self.__redirect_to_overview()

        self.deadline_has_expired = self.__deadline_has_expired()
        if self.deadline_has_expired == 'hard':
            if self.request.method == 'GET':
                return self.__redirect_to_overview()
            else:
                return self.render_to_response(self.get_context_data())
        return super(AddDeliveryView, self).dispatch(request, *args, **kwargs)

    def __deadline_has_expired(self):
        assignment = self.group.parentnode
        if self.group.last_deadline_datetime < datetime.now():
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
            uploadedfiles = [data['file'] for data in filemetaformset.cleaned_data if 'file' in data]
            if len(uploadedfiles) == 0:
                return self.render_to_response(self.get_context_data(
                    no_files_selected=True))
            else:
                if self.deadline_has_expired == 'soft':
                    add_delivery_form = AddDeliveryForm(self.request.POST)
                    confirm_delivery_after_soft_deadline = False
                    if add_delivery_form.is_valid():
                        confirm_delivery_after_soft_deadline = add_delivery_form\
                            .cleaned_data['confirm_delivery_after_soft_deadline']
                    if not confirm_delivery_after_soft_deadline:
                        return self.render_to_response(self.get_context_data(
                            delivery_after_soft_deadline_not_confirmed=True))

                return self.form_valid(uploadedfiles)
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
            deadline_id=self.group.last_deadline_id,
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

    def form_valid(self, uploadedfiles):
        delivery = self.__create_delivery()
        for uploadedfile in uploadedfiles:
            self.__create_filemeta(
                delivery=delivery,
                uploadedfile=uploadedfile,
                filename=uploadedfile.name)
        return HttpResponseRedirect(self.get_success_url(delivery))

    def get_context_data(self, **kwargs):
        context = super(AddDeliveryView, self).get_context_data(**kwargs)
        FileMetaFormSet = formset_factory(FileMetaForm, extra=3)
        filemetaformset = FileMetaFormSet()
        context['filemetaformset'] = filemetaformset
        context['deadline_has_expired'] = self.deadline_has_expired
        context['group'] = self.group
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', AddDeliveryView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
