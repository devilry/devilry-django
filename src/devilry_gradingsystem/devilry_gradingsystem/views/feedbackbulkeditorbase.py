from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.views.generic import FormView
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest

from devilry.apps.markup.parse_markdown import markdown_full
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import StaticFeedback
from devilry_gradingsystem.models import FeedbackDraft
from devilry_gradingsystem.widgets.editmarkdown import EditMarkdownLayoutObject
from devilry_gradingsystem.widgets.editfeedbackbuttonbar import EditFeedbackButtonBar

def get_redirect_url(draft_ids):
    pass


class FeedbackBulkEditorAssignmentObjectMixin(SingleObjectMixin):
    """
    Mixin that provides:

    - An Assignment object.
    - Authorization for access to the Assignment object.

    If your are creating a grading system plugin, you should NOT USE THIS
    directly. Use :class:`.FeedbackBulkEditorMixin` instead. 
    """
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackBulkEditorAssignmentObjectMixin, self).dispatch(*args, **kwargs)

    def _setup_common_data(self):
        self.object = self.get_object()
        self.assignment = self.object

    def get(self, *args, **kwargs):
        self._setup_common_data()
        assignment = self.object
        if not assignment.has_valid_grading_setup():
            return redirect('devilry_examiner_singledeliveryview', deliveryid=self.delivery.id)
        return super(FeedbackBulkEditorAssignmentObjectMixin, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        print "Post after dispatch?"
        self._setup_common_data()
        assignment = self.object
        if not assignment.has_valid_grading_setup():
            return HttpResponseBadRequest('Grading system is not set up correctly')
        return super(FeedbackBulkEditorAssignmentObjectMixin, self).post(*args, **kwargs)


    def get_queryset(self):
        """
        Ensure we only match assignments where the current user has access
        as an examiner.
        """
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(FeedbackBulkEditorAssignmentObjectMixin, self).get_context_data(**kwargs)
        assignment = self.object
        context['valid_grading_system_setup'] = assignment.has_valid_grading_setup()
        return context



class FeedbackBulkEditorMixin(FeedbackBulkEditorAssignmentObjectMixin):
    """
    Base mixin class for all feedback editor views.
    """

    def get_success_url(self):
        return reverse('devilry_examiner_allgroupsoverview',
            kwargs={'assignmentid': self.assignment.id})

    def create_feedbackdraft(self, points, feedbacktext_raw, feedbacktext_html, publish=False):


        ids = self.request.GET.getlist('edit')
        groups = AssignmentGroup.objects.get_queryset().filter(id__in=ids)
        draft = None
        draft_ids = []

        for group in groups:
            delivery = group.get_active_deadline().query_successful_deliveries()[0]
            draft = FeedbackDraft(
                delivery=delivery,
                points=points,
                feedbacktext_raw=feedbacktext_raw,
                feedbacktext_html=feedbacktext_html,
                saved_by=self.request.user
            )
            if publish:
                draft.published = True
                draft.staticfeedback = draft.to_staticfeedback()
                draft.staticfeedback.full_clean()
                draft.staticfeedback.save()
            draft.save()
            draft_ids.append(draft.id)
        return {'draft': draft, 'draft_ids': draft_ids}


class FeedbackBulkEditorFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FeedbackBulkEditorFormBase, self).__init__(*args, **kwargs)
        self._add_feedbacktext_field()

    def _add_feedbacktext_field(self):

        feedbacktext_editor = FeedbackDraft.DEFAULT_FEEDBACKTEXT_EDITOR
        self.fields['feedbacktext'] = forms.CharField(
            label=_('Feedback text'),
            required=False)

    def get_feedbacktext_layout_elements(self):
        return [EditMarkdownLayoutObject()]

    def get_submitbuttons_layout_elements(self):
        return [EditFeedbackButtonBar()]

    def add_common_layout_elements(self):
        for element in self.get_feedbacktext_layout_elements():
            self.helper.layout.append(element)
        for element in self.get_submitbuttons_layout_elements():
            self.helper.layout.append(element)



class FeedbackBulkEditorFormView(FeedbackBulkEditorMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super(FeedbackBulkEditorFormView, self).get_form_kwargs()
        return kwargs

    def get_success_url(self):
        publish = 'submit_publish' in self.request.POST
        if publish:
            return super(FeedbackBulkEditorFormView, self).get_success_url()
        else:
            return self.request.path

    def get_points_from_form(self, form):
        raise NotImplementedError()

    def get_create_feedbackdraft_kwargs(self, form, publish):
        return {
           'feedbacktext_raw': form.cleaned_data['feedbacktext'],
           'feedbacktext_html': markdown_full(form.cleaned_data['feedbacktext']),
           'publish': publish,
           'points': self.get_points_from_form(form)
        }


    def _get_preview_redirect_url(self, drafts, grouplist):
       return "{}?{}&{}".format(reverse('devilry_gradingsystem_feedbackdraft_bulkpreview',
                                              kwargs={'assignmentid': self.object.id, 
                                                      'draftid': drafts['draft'].id}), 
                               urlencode([('draftid', drafts['draft_ids'])], doseq=True),
                               urlencode(grouplist, doseq=True))

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

        drafts = self.create_feedbackdraft(**self.get_create_feedbackdraft_kwargs(form, publish))

        if preview:
            return redirect(self._get_preview_redirect_url(drafts, self.request.GET))
        else:
            return super(FeedbackBulkEditorFormView, self).form_valid(form)


    def get_initial_from_draft(self, draft):
        return {
            'feedbacktext': draft.feedbacktext_raw
        }

    def get_initial(self):
        draftid = self.request.GET.get('draftid', False)
        if draftid:
            draft = FeedbackDraft.objects.get(id=draftid)
            return self.get_initial_from_draft(draft)
        else:
            return {
                'feedbacktext': '',
                'points': False
            }
