from crispy_forms import layout
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import defaultfilters
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.views.generic import FormView
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden

from devilry.apps.core.templatetags.devilry_core_tags import devilry_user_displayname
from devilry.devilry_gradingsystem.widgets.filewidget import FeedbackEditorFileWidget
from devilry.devilry_markup.parse_markdown import markdown_full
from devilry.apps.core.models import Delivery
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile
from devilry.devilry_gradingsystem.widgets.editmarkdown import EditMarkdownLayoutObject
from devilry.devilry_gradingsystem.widgets.editfeedbackbuttonbar import EditFeedbackButtonBar, \
    EditFeedbackButtonBarSaveDraftOnly


class FeedbackEditorSingleDeliveryObjectMixin(SingleObjectMixin):
    """
    Mixin that provides:

    - A delivery object.
    - Authorization for access to the delivery object.

    If your are creating a grading system plugin, you should NOT USE THIS
    directly. Use :class:`.FeedbackEditorMixin` instead. 
    """
    model = Delivery
    pk_url_kwarg = 'deliveryid'
    context_object_name = 'delivery'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackEditorSingleDeliveryObjectMixin, self).dispatch(*args, **kwargs)

    def _setup_common_data(self):
        self.object = self.get_object()
        self.delivery = self.object
        self.assignment = self.delivery.deadline.assignment_group.assignment
        self.last_draft = FeedbackDraft.get_last_feedbackdraft(
            assignment=self.assignment,
            delivery=self.delivery,
            user=self.request.user)
        self.last_feedbackdraftfile = FeedbackDraftFile.objects\
            .filter_accessible_files(
                assignment=self.assignment,
                delivery=self.delivery,
                user=self.request.user)\
            .first()

    def get(self, *args, **kwargs):
        self._setup_common_data()
        if self.last_draft:
            messages.info(self.request, _('Loaded draft saved %(save_datetime)s by %(user)s.') % {
                'user': devilry_user_displayname(self.last_draft.saved_by),
                'save_datetime': defaultfilters.date(self.last_draft.save_timestamp, 'SHORT_DATETIME_FORMAT'),
            })
        if not self.assignment.has_valid_grading_setup():
            return redirect('devilry_examiner_singledeliveryview', deliveryid=self.delivery.id)
        return super(FeedbackEditorSingleDeliveryObjectMixin, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._setup_common_data()
        if not self.assignment.has_valid_grading_setup():
            return HttpResponseBadRequest('Grading system is not set up correctly')
        return super(FeedbackEditorSingleDeliveryObjectMixin, self).post(*args, **kwargs)

    def get_queryset(self):
        """
        Ensure we only match deliveries where the current user has access
        as an examiner.
        """
        return Delivery.objects.filter_examiner_has_access(self.request.user)\
            .select_related( # Use select_related to lookup all the related objects in the query
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode', # Assignment
                'deadline__assignment_group__parentnode__parentnode', # Period
                'deadline__assignment_group__parentnode__parentnode__parentnode') # Subject

    def get_context_data(self, **kwargs):
        context = super(FeedbackEditorSingleDeliveryObjectMixin, self).get_context_data(**kwargs)
        delivery = self.object
        assignment = delivery.deadline.assignment_group.assignment
        context['valid_grading_system_setup'] = assignment.has_valid_grading_setup()
        return context


class FeedbackEditorMixin(FeedbackEditorSingleDeliveryObjectMixin):
    """
    Base mixin class for all feedback editor views.
    """

    def get_success_url(self):
        return reverse('devilry_examiner_singledeliveryview', kwargs={'deliveryid': self.delivery.id})

    def create_feedbackdraft(self, points, feedbacktext_raw, feedbacktext_html,
                             feedbackfile_uploadedfile, feedbackfile_has_changed,
                             publish=False):
        draft = FeedbackDraft(
            delivery=self.delivery,
            points=points,
            feedbacktext_raw=feedbacktext_raw,
            feedbacktext_html=feedbacktext_html,
            saved_by=self.request.user
        )

        if feedbackfile_has_changed:
            if self.last_feedbackdraftfile:
                self.last_feedbackdraftfile.file.delete()
                self.last_feedbackdraftfile.delete()
            if feedbackfile_uploadedfile:
                feedbackdraftfile = FeedbackDraftFile(
                    delivery=self.delivery,
                    saved_by=self.request.user,
                    filename=feedbackfile_uploadedfile.name)
                feedbackdraftfile.file.save(feedbackfile_uploadedfile.name, feedbackfile_uploadedfile)
                self.last_feedbackdraftfile = feedbackdraftfile

        if publish:
            draft.published = True
            staticfeedback = draft.to_staticfeedback()
            staticfeedback.full_clean()
            staticfeedback.save()
            draft.staticfeedback = staticfeedback
            if self.last_feedbackdraftfile:
                self.last_feedbackdraftfile.to_staticfeedbackfileattachment(
                    staticfeedback=draft.staticfeedback)
        draft.save()
        return draft


class FeedbackEditorFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self.last_draft = kwargs.pop('last_draft')
        self.assignment = kwargs.pop('assignment')
        self.feedbackfile = kwargs.pop('feedbackfile')
        super(FeedbackEditorFormBase, self).__init__(*args, **kwargs)
        self._add_feedbacktext_field()

    def _add_feedbacktext_field(self):
        # if self.last_draft:
        #     feedbacktext_editor = self.last_draft.feedbacktext_editor
        # else:
        #     feedbacktext_editor = FeedbackDraft.DEFAULT_FEEDBACKTEXT_EDITOR
        self.fields['feedbacktext'] = forms.CharField(
            label=_('Feedback text (optional)'),
            required=False)

        feedbackfile_helptext = None
        # if self.feedbackfile:
        #     feedbackfile_helptext = _('')
        self.fields['feedbackfile'] = forms.FileField(
            label=_('Attach a file file to your feedback (optional)'),
            required=False,
            help_text=feedbackfile_helptext,
            widget=FeedbackEditorFileWidget(feedbackfile=self.feedbackfile))

    def get_feedbacktext_layout_elements(self):
        return [
            EditMarkdownLayoutObject(),
            layout.Div(
                layout.Field('feedbackfile'),
                css_class='devilry-gradingsystem-feedbackeditor-feedbackfile-wrapper')
        ]

    def get_submitbuttons_layout_elements(self):
        if self.assignment.feedback_workflow_allows_examiners_publish_feedback():
            return [EditFeedbackButtonBar()]
        else:
            return [EditFeedbackButtonBarSaveDraftOnly()]

    def add_common_layout_elements(self):
        for element in self.get_feedbacktext_layout_elements():
            self.helper.layout.append(element)
        for element in self.get_submitbuttons_layout_elements():
            self.helper.layout.append(element)


class FeedbackEditorFormView(FeedbackEditorMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super(FeedbackEditorFormView, self).get_form_kwargs()
        kwargs['last_draft'] = self.last_draft
        kwargs['assignment'] = self.delivery.deadline.assignment_group.assignment
        kwargs['feedbackfile'] = self.last_feedbackdraftfile
        return kwargs

    def get_success_url(self):
        publish = 'submit_publish' in self.request.POST
        if publish:
            return super(FeedbackEditorFormView, self).get_success_url()
        else:
            return self.request.path

    def get_points_from_form(self, form):
        raise NotImplementedError()

    def get_create_feedbackdraft_kwargs(self, form, publish):
        return {
            'feedbacktext_raw': form.cleaned_data['feedbacktext'],
            'feedbacktext_html': markdown_full(form.cleaned_data['feedbacktext']),
            'publish': publish,
            'points': self.get_points_from_form(form),
            'feedbackfile_uploadedfile': form.cleaned_data['feedbackfile'],
            'feedbackfile_has_changed': 'feedbackfile' in form.changed_data
        }

    def save_pluginspecific_state(self, form):
        """
        Save extra state that is specific to this plugin. I.E: Input from
        users that has no corresponding field in FeedbackDraft, and has to be
        stored in the data models for the plugin.
        """
        pass

    def form_valid(self, form):
        publish = 'submit_publish' in self.request.POST
        preview = 'submit_preview' in self.request.POST
        save_and_exit = 'submit_save_and_exit' in self.request.POST

        if publish and not self.assignment.feedback_workflow_allows_examiners_publish_feedback():
            return HttpResponseForbidden()

        self.save_pluginspecific_state(form)
        draft = self.create_feedbackdraft(**self.get_create_feedbackdraft_kwargs(form, publish))
        if preview:
            return redirect(
                'devilry_gradingsystem_feedbackdraft_preview',
                deliveryid=self.delivery.id,
                draftid=draft.id)
        elif save_and_exit:
            return redirect(
                'devilry_examiner_singledeliveryview',
                deliveryid=self.delivery.id)
        else:
            return super(FeedbackEditorFormView, self).form_valid(form)

    def get_initial_from_last_draft(self):
        return {
            'feedbacktext': self.last_draft.feedbacktext_raw
        }

    def get_initial(self):
        initial = {}
        if self.last_draft:
            initial = self.get_initial_from_last_draft()
            if self.last_feedbackdraftfile:
                initial['feedbackfile'] = self.last_feedbackdraftfile.file
        return initial
