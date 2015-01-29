from datetime import datetime
import uuid
from crispy_forms import layout
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django_cradmin import crapp
from django_cradmin.apps.cradmin_temporaryfileuploadstore.crispylayouts import BulkFileUploadSubmit
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection, TemporaryFile
from django_cradmin.apps.cradmin_temporaryfileuploadstore.widgets import BulkFileUploadWidget
from django_cradmin.viewhelpers import formbase
from devilry.apps.core.models import Assignment, Candidate, Delivery, FileMeta


DEFAULT_DEADLINE_EXPIRED_MESSAGE = _('Your active deadline, {deadline} has expired, and the administrators of {assignment} have configured HARD deadlines. This means that you can not add more deliveries to this assignment before an administrator have extended your deadline.')
DEADLINE_EXPIRED_MESSAGE = getattr(settings, 'DEVILRY_DEADLINE_EXPIRED_MESSAGE', DEFAULT_DEADLINE_EXPIRED_MESSAGE)
DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES = getattr(settings, 'DELIVERY_DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES', 120)


# class FileMetaForm(forms.Form):
#     file = forms.FileField(
#         label=_('Upload a file'))


class AddDeliveryView(formbase.FormView):
    template_name = 'devilry_student/cradmin_group/add_delivery.django.html'
    form_attributes = {
        'django-cradmin-bulkfileupload-form': ''
    }
    form_id = 'devilry_student_add_delivery_form'
    extra_form_css_classes = ['django-cradmin-form-noasterisk']

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

    def get_form_class(self):
        class AddDeliveryForm(forms.Form):
            confirm_delivery_after_soft_deadline = forms.BooleanField(
                required=bool(self.deadline_has_expired),
                label=_('I want to add a delivery after the deadline has expired.'),
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
                    # dropbox_text=_('Upload images by dragging and dropping them here'),
                    # invalid_filetype_message=_('Invalid filetype. You can only upload images.'),
                    # advanced_fileselectbutton_text=_('... or select images'),
                    # simple_fileselectbutton_text=_('Select images ...')
                ),
                label=_('Upload at least one file and click "Add delivery"'),
                help_text=_(
                    'Upload as many files as you like.'),
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

    def __deadline_has_expired(self):
        assignment = self.group.parentnode
        if self.group.last_deadline_datetime < datetime.now():
            if assignment.deadline_handling == Assignment.DEADLINEHANDLING_HARD:
                return 'hard'
            else:
                return 'soft'
        else:
            return False

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

    def __create_unique_filename(self, filenames, filename):
        if filename in filenames:
            new_filename = u'{}-{}'.format(str(uuid.uuid4()), filename)
            if new_filename in filenames:
                return self.__create_unique_filename(filenames, filename)
            else:
                return new_filename
        else:
            return filename

    def get_context_data(self, **kwargs):
        context = super(AddDeliveryView, self).get_context_data(**kwargs)
        # FileMetaFormSet = formset_factory(FileMetaForm, extra=3)
        # filemetaformset = FileMetaFormSet(prefix='filemeta_formset')
        # context['filemetaformset'] = filemetaformset
        context['deadline_has_expired'] = self.deadline_has_expired
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
                layout.HTML('<p>'),
                layout.HTML(
                    _('Do you really want to add a delivery after the deadline? You normally '
                      'need to have a valid reason when adding deadline after the deadline.')),
                layout.HTML('</p>'),
                'confirm_delivery_after_soft_deadline'
            ))
        return fieldlayout

    # def get_formhelper(self):
    #     formhelper = super(AddDeliveryView, self).get_formhelper()
    #     formhelper.form_show_labels = False
    #     return formhelper

    def __turn_temporaryfile_into_filemeta(self, temporaryfile, delivery, filename):
        delivery.add_file(filename, temporaryfile.file.chunks())

    def __turn_temporaryfiles_into_delivery(self, temporaryfilecollection):
        delivery = self.__create_delivery()
        filenames = set()
        for temporaryfile in temporaryfilecollection.files.all():
            filename = self.__create_unique_filename(filenames, temporaryfile.filename)
            filenames.add(filename)
            self.__turn_temporaryfile_into_filemeta(
                temporaryfile=temporaryfile,
                delivery=delivery,
                filename=filename)

        return delivery

    def get_collectionqueryset(self):
        return TemporaryFileCollection.objects\
            .filter_for_user(self.request.user)\
            .prefetch_related('files')

    def form_valid(self, form):
        collectionid = form.cleaned_data['filecollectionid']
        try:
            temporaryfilecollection = self.get_collectionqueryset().get(id=collectionid)
        except TemporaryFileCollection.DoesNotExist:
            return HttpResponseNotFound()
        else:
            delivery = self.__turn_temporaryfiles_into_delivery(temporaryfilecollection)
            return HttpResponseRedirect(self.get_success_url(delivery))

    # def form_valid(self, uploadedfiles):
    #     delivery = self.__create_delivery()
    #     filenames = set()
    #     for uploadedfile in uploadedfiles:
    #         filename = self.__create_unique_filename(filenames, uploadedfile.name)
    #         filenames.add(filename)
    #         self.__create_filemeta(
    #             delivery=delivery,
    #             uploadedfile=uploadedfile,
    #             filename=filename)
    #     return HttpResponseRedirect(self.get_success_url(delivery))

    # def post(self, *args, **kwargs):
    #     FileMetaFormSet = formset_factory(FileMetaForm)
    #     filemetaformset = FileMetaFormSet(self.request.POST, self.request.FILES, prefix='filemeta_formset')
    #     if filemetaformset.is_valid():
    #         uploadedfiles = [data['file'] for data in filemetaformset.cleaned_data if 'file' in data]
    #         if len(uploadedfiles) == 0:
    #             return self.render_to_response(self.get_context_data(
    #                 no_files_selected=True))
    #         else:
    #             if self.deadline_has_expired == 'soft':
    #                 add_delivery_form = AddDeliveryForm(self.request.POST)
    #                 confirm_delivery_after_soft_deadline = False
    #                 if add_delivery_form.is_valid():
    #                     confirm_delivery_after_soft_deadline = add_delivery_form\
    #                         .cleaned_data['confirm_delivery_after_soft_deadline']
    #                 if not confirm_delivery_after_soft_deadline:
    #                     return self.render_to_response(self.get_context_data(
    #                         delivery_after_soft_deadline_not_confirmed=True))
    #
    #             return self.form_valid(uploadedfiles)
    #     else:
    #         raise Exception('Getting here should not be possible.')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', AddDeliveryView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
