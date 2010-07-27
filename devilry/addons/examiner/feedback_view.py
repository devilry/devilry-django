from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from devilry.core.models import Feedback
from django import forms


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text', 'format', 'feedback_published')
        widgets = {
                'text': forms.Textarea(attrs={'cols': 90, 'rows': 25})
        }

def parse_feedback_form(request, delivery_obj, prefix='feedback'):
    try:
        feedback_obj = delivery_obj.feedback
    except Feedback.DoesNotExist, e:
        feedback_obj = Feedback(delivery=delivery_obj)

    if request.method == 'POST':
        return FeedbackForm(request.POST, instance=feedback_obj, prefix=prefix)
    else:
        return FeedbackForm(instance=feedback_obj, prefix=prefix)

def redirect_after_successful_save(delivery_obj):
    return HttpResponseRedirect(
            reverse('devilry-examiner-correct_delivery',
                args=(delivery_obj.id,)))

def render_response(request, delivery_obj, feedback_form, grade_form,
        template_path='devilry/examiner/correct_delivery.django.html'):
    return render_to_response(template_path, {
            'delivery': delivery_obj,
            'feedback_form': feedback_form,
            'grade_form': grade_form,
        }, context_instance=RequestContext(request))


def view_shortcut(request, delivery_obj, model_cls, form_cls):
    feedback_form = parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.content_object:
        grade_obj = feedback_obj.content_object
    else:
        grade_obj = model_cls()

    if request.method == 'POST':
        grade_form = form_cls(request.POST, instance=grade_obj, prefix='grade')
    else:
        grade_form = form_cls(instance=grade_obj, prefix='grade')

    if request.method == 'POST':
        if feedback_form.is_valid() and grade_form.is_valid():
            grade_form.save()
            feedback_form.instance.content_object = grade_form.instance
            feedback_form.save()
            return redirect_after_successful_save(delivery_obj)

    return render_response(request, delivery_obj,
            feedback_form, grade_form)
