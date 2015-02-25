from datetime import datetime
from django.db.models import Q
from django.dispatch import Signal
from django.shortcuts import get_object_or_404
from django_cradmin import crinstance

from django.views.generic import DetailView
from django_cradmin.viewhelpers import objecttable
from crispy_forms import layout
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_cradmin import crapp
from django_cradmin.apps.cradmin_temporaryfileuploadstore.crispylayouts import BulkFileUploadSubmit
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection, TemporaryFile
from django_cradmin.apps.cradmin_temporaryfileuploadstore.widgets import BulkFileUploadWidget
from django_cradmin.viewhelpers import formbase

from devilry.apps.core.models import Candidate, Delivery, FileMeta, Deadline
from devilry.devilry_student.cradmin_group.utils import check_if_last_deadline_has_expired
from devilry.apps.core.models import deliverytypes


DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES = getattr(settings, 'DELIVERY_DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES', 120)

#: This signal is sent on successful delivery.
successful_delivery_signal = Signal(providing_args=["delivery"])


class DeliveryNumberColumn(objecttable.SingleActionColumn):
    modelfield = 'number'
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery-number-column.django.html'
    context_object_name = 'delivery'

    def get_header(self):
        return _('Delivery')

    def get_actionurl(self, delivery):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='deliveries',
            roleid=delivery.deadline.assignment_group_id,
            viewname='deliverydetails',
            kwargs={'pk': delivery.pk}
        )

    def is_sortable(self):
        return False


class DeliveryStatusColumn(objecttable.PlainTextColumn):
    modelfield = 'id'
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery-status-column.django.html'
    context_object_name = 'delivery'

    def get_header(self):
        return _('Status')

    def is_sortable(self):
        return False


class QuerySetForRoleMixin(object):
    def get_queryset_for_role(self, group):
        return Delivery.objects\
            .filter(deadline__assignment_group=group)\
            .select_related('deadline', 'feedback')


class DeliveryListView(QuerySetForRoleMixin, objecttable.ObjectTableView):
    model = Delivery
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery_list.django.html'
    context_object_name = 'deliveries'

    columns = [
        DeliveryNumberColumn,
        DeliveryStatusColumn,
    ]

    def get_queryset(self):
        return super(DeliveryListView, self).get_queryset()\
            .filter(
                Q(delivery_type=deliverytypes.ELECTRONIC) |
                Q(last_feedback__isnull=False))

    def get_pagetitle(self):
        return _('Deliveries')


class DeliveryDetailsView(QuerySetForRoleMixin, DetailView):
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery_details.django.html'
    context_object_name = 'delivery'

    def get_queryset(self):
        return self.get_queryset_for_role(self.request.cradmin_role)\
            .select_related('deadline')\
            .prefetch_related('filemetas')

    def get_context_data(self, **kwargs):
        context = super(DeliveryDetailsView, self).get_context_data(**kwargs)
        context['group'] = self.request.cradmin_role

        # Fetch filemetas so we do not need to query an extra time to
        # check if we have any filemetas
        context['filemetas'] = list(context['delivery'].filemetas.all())

        return context


class AddDeliveryView(formbase.FormView):
    template_name = 'devilry_student/cradmin_group/add_delivery.django.html'
    form_attributes = {
        'django-cradmin-bulkfileupload-form': ''
    }
    form_id = 'devilry_student_add_delivery_form'
    extra_form_css_classes = ['django-cradmin-form-noasterisk']

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

        self.deadline_has_expired = check_if_last_deadline_has_expired(self.group)
        if self.deadline_has_expired == 'hard':
            if self.request.method == 'GET':
                return self.__redirect_to_overview()
            else:
                return self.render_to_response(self.get_context_data())
        return super(AddDeliveryView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        class AddDeliveryForm(forms.Form):
            confirm_delivery_after_soft_deadline = forms.BooleanField(
                required=bool(self.deadline_has_expired),
                label=_('I want to add a delivery after the deadline has expired.'),
                help_text=_('Do you really want to add a delivery after the deadline? You normally '
                            'need to have a valid reason when adding a delivery after the deadline.'),
                error_messages={
                    'required': _('You must confirm that you want to add a delivery after the deadline has expired.')
                })

            filecollectionid = forms.IntegerField(
                required=True,
                widget=BulkFileUploadWidget(
                    apiparameters={
                        'unique_filenames': True,
                        'max_filename_length': FileMeta.MAX_FILENAME_LENGTH
                    }
                ),
                label=_('Upload at least one file and click "Add delivery"'),
                help_text=_(
                    _('Upload as many files as you like.')),
                error_messages={
                    'required': _('You have to add at least one file to make a delivery.')
                })

            def clean_filecollectionid(self):
                filecollectionid = self.cleaned_data['filecollectionid']
                if filecollectionid is not None:
                    # This may be used to check for existing files in any filecollectionid,
                    # but that should not be a problem since it does not tell users anything
                    # useful.
                    if TemporaryFile.objects\
                            .filter(collection_id=filecollectionid)\
                            .count() < 1:
                        raise forms.ValidationError(_('You have to add at least one file to make a delivery.'))
                return filecollectionid

        return AddDeliveryForm

    def __get_canidate(self):
        try:
            return self.group.candidates.get(student=self.request.user)
        except Candidate.DoesNotExist:
            return None

    def get_success_url(self, delivery):
        return self.request.cradmin_app.reverse_appurl('deliverydetails', kwargs={
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

    def get_context_data(self, **kwargs):
        context = super(AddDeliveryView, self).get_context_data(**kwargs)
        context['deadline_has_expired'] = self.deadline_has_expired
        context['last_deadline'] = get_object_or_404(Deadline, pk=self.group.last_deadline_pk)
        context['group'] = self.group
        return context

    def get_buttons(self):
        return [
            BulkFileUploadSubmit(
                'submit', _('Add delivery'),
                uploading_text=_('Uploading files'),
                uploading_icon_cssclass='fa fa-spinner fa-spin'),
        ]

    def get_field_layout(self):
        fieldlayout = [
            layout.Div(
                'filecollectionid',
                css_class="cradmin-focusfield"),
        ]
        if self.deadline_has_expired:
            fieldlayout.append(layout.Fieldset(
                _('Deadline has expired'),
                'confirm_delivery_after_soft_deadline'
            ))
        return fieldlayout

    def __turn_temporaryfile_into_filemeta(self, temporaryfile, delivery):
        delivery.add_file(temporaryfile.filename, temporaryfile.file.chunks())

    def __turn_temporaryfiles_into_delivery(self, temporaryfilecollection):
        delivery = self.__create_delivery()
        for temporaryfile in temporaryfilecollection.files.all():
            self.__turn_temporaryfile_into_filemeta(
                temporaryfile=temporaryfile,
                delivery=delivery)

        return delivery

    def get_collectionqueryset(self):
        return TemporaryFileCollection.objects\
            .filter_for_user(self.request.user)\
            .prefetch_related('files')

    def on_successful_delivery(self, delivery):
        successful_delivery_signal.send_robust(sender=delivery, delivery=delivery)

    def form_valid(self, form):
        collectionid = form.cleaned_data['filecollectionid']
        try:
            temporaryfilecollection = self.get_collectionqueryset().get(id=collectionid)
        except TemporaryFileCollection.DoesNotExist:
            return HttpResponseNotFound()
        else:
            delivery = self.__turn_temporaryfiles_into_delivery(temporaryfilecollection)
            temporaryfilecollection.clear_files_and_delete()
            self.on_successful_delivery(delivery)
            return HttpResponseRedirect(self.get_success_url(delivery))


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            DeliveryListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^delivery/(?P<pk>\d+)$',
            DeliveryDetailsView.as_view(),
            name='deliverydetails'),
        crapp.Url(
            r'^add$',
            AddDeliveryView.as_view(),
            name='add-delivery')
    ]
