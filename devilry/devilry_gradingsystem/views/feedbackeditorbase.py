from django.core.urlresolvers import reverse
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.views.generic import FormView
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django_cradmin.widgets import filewidgets
from devilry.devilry_gradingsystem.widgets.filewidget import FeedbackEditorFileWidget

from devilry.devilry_markup.parse_markdown import markdown_full
from devilry.apps.core.models import Delivery
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile
from devilry.devilry_gradingsystem.widgets.editmarkdown import EditMarkdownLayoutObject
from devilry.devilry_gradingsystem.widgets.editfeedbackbuttonbar import EditFeedbackButtonBar


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
        self.last_feedbackfile = None
        self.last_draft = self.delivery.devilry_gradingsystem_feedbackdraft_set.first()
        if self.last_draft:
            self.last_feedbackfile = FeedbackDraftFile.objects\
                .filter(delivery=self.delivery, saved_by=self.request.user)\
                .first()

    def get(self, *args, **kwargs):
        self._setup_common_data()
        assignment = self.delivery.deadline.assignment_group.assignment
        if not assignment.has_valid_grading_setup():
            return redirect('devilry_examiner_singledeliveryview', deliveryid=self.delivery.id)
        return super(FeedbackEditorSingleDeliveryObjectMixin, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._setup_common_data()
        assignment = self.delivery.deadline.assignment_group.assignment
        if not assignment.has_valid_grading_setup():
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
        return reverse('devilry_examiner_singledeliveryview',
            kwargs={'deliveryid': self.delivery.id})

    def create_feedbackdraft(self, points, feedbacktext_raw, feedbacktext_html, feedbackfile, publish=False):
        draft = FeedbackDraft(
            delivery=self.delivery,
            points=points,
            feedbacktext_raw=feedbacktext_raw,
            feedbacktext_html=feedbacktext_html,
            saved_by=self.request.user
        )

        if feedbackfile:
            feedbackdraftfile = FeedbackDraftFile(
                delivery=self.delivery,
                saved_by=self.request.user,
                filename=feedbackfile.name)
            feedbackdraftfile.file.save(feedbackfile.name, feedbackfile)

        if publish:
            draft.published = True
            draft.staticfeedback = draft.to_staticfeedback()
            draft.staticfeedback.full_clean()
            draft.staticfeedback.save()
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
            label=_('Feedback text'),
            required=False)

        self.fields['feedbackfile'] = forms.FileField(
            label=_('Feedback file'),
            required=False,
            widget=FeedbackEditorFileWidget(feedbackfile=self.feedbackfile))

    def get_feedbacktext_layout_elements(self):
        return [EditMarkdownLayoutObject(), 'feedbackfile']

    def get_submitbuttons_layout_elements(self):
        return [EditFeedbackButtonBar()]

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
        kwargs['feedbackfile'] = self.last_feedbackfile
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
        print
        print "*" * 70
        print
        print self.request.POST
        print form.cleaned_data
        print
        print "*" * 70
        print

        return {
           'feedbacktext_raw': form.cleaned_data['feedbacktext'],
           'feedbacktext_html': markdown_full(form.cleaned_data['feedbacktext']),
           'publish': publish,
           'points': self.get_points_from_form(form),
           'feedbackfile': form.cleaned_data['feedbackfile']
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
        self.save_pluginspecific_state(form)
        draft = self.create_feedbackdraft(**self.get_create_feedbackdraft_kwargs(form, publish))
        if preview:
            return redirect('devilry_gradingsystem_feedbackdraft_preview',
                deliveryid=self.delivery.id,
                draftid=draft.id)
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
            if self.last_feedbackfile:
                initial['feedbackfile'] = self.last_feedbackfile.file
            # print
            # print "*" * 70
            # print
            # print last_feedbackfile
            # print initial
            # print
            # print "*" * 70
            # print

        return initial
