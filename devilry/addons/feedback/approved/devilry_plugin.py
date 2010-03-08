from devilry.examinerview import feedback_view
from django import forms
from devilry.core.models import Feedback
from django.utils.translation import ugettext as _


class ApprovedFeedbackView(feedback_view.FeedbackView):
    grade_choices = (
        ('approved', _('Approved')),
        ('not approved', _('Not approved'))
    )
    @classmethod
    def create_form_obj(cls, request, feeback_obj):
        class CorrectForm(forms.ModelForm):
            grade = forms.ChoiceField(
                    choices=cls.grade_choices)
            class Meta:
                model = Feedback
                fields = ('grade', 'feedback_text', 'feedback_format', 'feedback_published')
        if request.method == 'POST':
            return CorrectForm(request.POST, instance=feeback_obj)
        else:
            return CorrectForm(instance=feeback_obj)

    @classmethod
    def save(cls, form):
        form.save()
        return cls.redirect_after_successful_save(form)

feedback_view.register(ApprovedFeedbackView)
