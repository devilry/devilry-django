from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404

from devilry.apps.core.models import Delivery
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile


class StaticFeedbackPreviewMock(object):
    """
    Mocks the parts of a :class:`devilry.apps.core.models.StaticFeedback`
    that is needed to create a preview.

    We use this to avoid having to save a StaticFeedback before we
    preview it. Note that the only reasons why we need this wrapper
    is because:

    1. We want to use the same template to render the preview
       as we use to render the actual feedback.
    2. We can not set the ``filess``-attribute of an unsaved
       StaticFeedback.
    """
    def __init__(self, rendered_view, is_passing_grade, grade, files):
        self.rendered_view = rendered_view
        self.is_passing_grade = is_passing_grade
        self.grade = grade
        self.files = files


class FeedbackDraftPreviewView(DetailView):
    template_name = "devilry_gradingsystem/feedbackdraft_preview.django.html"
    model = Delivery
    pk_url_kwarg = 'deliveryid'
    context_object_name = 'delivery'

    def get_queryset(self):
        return Delivery.objects.filter_examiner_has_access(self.request.user)\
            .select_related( # Use select_related to lookup all the related objects in the query
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode', # Assignment
                'deadline__assignment_group__parentnode__parentnode', # Period
                'deadline__assignment_group__parentnode__parentnode__parentnode', # Subject
                )

    def get_feedbackdraft(self):
        delivery = self.object
        draftid = self.kwargs['draftid']
        try:
            return FeedbackDraft.objects.get(
                delivery=delivery,
                id=draftid)
        except FeedbackDraft.DoesNotExist:
            raise Http404('Feedback draft with ID={} does not exist.'.format(draftid))

    def get_context_data(self, **kwargs):
        context = super(FeedbackDraftPreviewView, self).get_context_data(**kwargs)

        delivery = context['object']
        draft = self.get_feedbackdraft()
        unsaved_staticfeedback = draft.to_staticfeedback()
        draftfiles = FeedbackDraftFile.objects.filter(
            saved_by=self.request.user, delivery=delivery)
        staticfeedbackmock = StaticFeedbackPreviewMock(
            rendered_view=unsaved_staticfeedback.rendered_view,
            grade=unsaved_staticfeedback.grade,
            is_passing_grade=unsaved_staticfeedback.is_passing_grade,
            # We send in a FeedbackDraftFile queryset. This works because it
            # has the same attributes as StaticFeedbackFileAttachment.
            files=draftfiles)

        context['staticfeedbackmock'] = staticfeedbackmock
        context['valid_grading_system_setup'] = True
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        delivery = self.object
        if 'submit_publish' in self.request.POST:
            draft = self.get_feedbackdraft()
            draft.published = True
            draft.staticfeedback = draft.to_staticfeedback()
            draft.staticfeedback.full_clean()
            draft.staticfeedback.save()
            last_feedbackdraftfile = FeedbackDraftFile.objects\
                .filter(delivery=delivery, saved_by=self.request.user)\
                .first()
            if last_feedbackdraftfile:
                last_feedbackdraftfile.to_staticfeedbackfileattachment(
                    staticfeedback=draft.staticfeedback)
            return redirect('devilry_examiner_singledeliveryview', deliveryid=delivery.id)
        else:
            return redirect(str(delivery.assignment.get_gradingsystem_plugin_api().get_edit_feedback_url(delivery.id)))
