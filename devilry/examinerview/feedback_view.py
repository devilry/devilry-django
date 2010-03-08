from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from devilry.core.models import Feedback
from django import forms



class FeedbackView(object):
    @classmethod
    def _get_key(cls):
        return '%s.%s' % (cls.__module__, cls.__name__)

    @classmethod
    def create_view(cls, request, delivery_obj):
        try:
            feedback_obj = delivery_obj.feedback
        except Feedback.DoesNotExist, e:
            feedback_obj = Feedback(delivery=delivery_obj)

        form = cls.create_form_obj(request, feedback_obj)
        if request.method == 'POST':
            if form.is_valid():
                return cls.save(form)

        formdict = {'delivery': delivery_obj, 'form': form}
        return cls.render_view(request, form, formdict)

    @classmethod
    def render_view(cls, request, form, formdict):
        return render_to_response('devilry/examinerview/correct_delivery.django.html',
            formdict, context_instance=RequestContext(request))

    @classmethod
    def redirect_after_successful_save(cls, form):
        return HttpResponseRedirect(
                reverse('devilry.examinerview.views.correct_delivery',
                    args=(form.instance.delivery.id,)))

    @classmethod
    def create_form_obj(cls, request, feeback_obj):
        class CorrectForm(forms.ModelForm):
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


_registry = {}
def register(cls):
    print cls._get_key()
    _registry[cls._get_key()] = cls

def get(name):
    return _registry[name]
