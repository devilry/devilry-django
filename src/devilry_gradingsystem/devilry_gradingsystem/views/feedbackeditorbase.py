# from django.core.urlresolvers import reverse
# from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
# from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.generic import FormView

from devilry.apps.core.models import Delivery
from devilry_gradingsystem.models import FeedbackDraft




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

    # TODO: Redirect on GET when not configured correctly!

    def set_delivery_and_last_draft(self):
        self.object = self.get_object()
        self.delivery = self.object
        self.last_draft = None
        if self.delivery.devilry_gradingsystem_feedbackdraft_set.count() > 0:
            self.last_draft = self.delivery.devilry_gradingsystem_feedbackdraft_set.all()[0]

    def get_success_url(self):
        return reverse('devilry_examiner_singledeliveryview',
            kwargs={'deliveryid': self.delivery.id})



class FeedbackEditorFormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self.last_draft = kwargs.pop('last_draft')
        super(FeedbackEditorFormBase, self).__init__(*args, **kwargs)
        self._add_feedbacktext_field()

    def _add_feedbacktext_field(self):
        if self.last_draft:
            feedbacktext_editor = self.last_draft.feedbacktext_editor
        else:
            feedbacktext_editor = FeedbackDraft.DEFAULT_FEEDBACKTEXT_EDITOR
        self.fields['feedbacktext'] = forms.CharField(widget=forms.Textarea)


class FeedbackEditorFormView(FeedbackEditorMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super(FeedbackEditorFormView, self).get_form_kwargs()
        kwargs['last_draft'] = self.last_draft
        return kwargs

    def get(self, *args, **kwargs):
        self.set_delivery_and_last_draft()
        return super(FeedbackEditorFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.set_delivery_and_last_draft()
        return super(FeedbackEditorFormView, self).get(*args, **kwargs)
