from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

from devilry.core.models import Feedback
from devilry.ui.widgets import RstEditWidget

from devilry.ui.messages import UiMessages
from django.utils.translation import ugettext as _
from devilry.core.devilry_email import send_email
from devilry.settings import WEB_PAGE_PREFIX
from devilry.settings import DEVILRY_MAIN_PAGE
from urlparse import urljoin

class FeedbackForm(forms.ModelForm):
    """ A ModelForm for the :class:`devilry.core.models.Feedback`-class. """
    class Meta:
        model = Feedback
        fields = ('text', 'format', 'published')
        widgets = {
                #'text': forms.Textarea(attrs={'cols': 90, 'rows': 25})
                'text': RstEditWidget
        }

def parse_feedback_form(request, delivery_obj, prefix='feedback'):
    try:
        feedback_obj = delivery_obj.feedback
    except Feedback.DoesNotExist, e:
        feedback_obj = Feedback(delivery=delivery_obj)
    feedback_obj.last_modified_by = request.user
    if request.method == 'POST':
        return FeedbackForm(request.POST, instance=feedback_obj, prefix=prefix)
    else:
        return FeedbackForm(instance=feedback_obj, prefix=prefix)

def redirect_after_successful_save(request, delivery_obj):
    if delivery_obj.feedback.published:
        assignment = delivery_obj.assignment_group.parentnode
        period = assignment.parentnode
        subject = period.parentnode
        
        email_message = _("Your delivery has been corrected." \
                          "\n\n" \
                          "Subject: %s\n" \
                          "Period: %s\n" \
                          "Assignment: %s\n") % (subject.long_name,
                                                 period.long_name,
                                                 assignment.long_name)
        
        cands = delivery_obj.assignment_group.candidates.all()
        users = []
        for candidate in cands:
            users.append(candidate.student)

        rev = reverse('devilry-student-show-delivery', args=(delivery_obj.id,))
        email_message += _("\nThe feedback can be viewed at:\n%s\n") % \
                         (request.build_absolute_uri(rev))
        send_email(users, 
                   _("New feedback - %s") % (assignment.get_path()), 
                   email_message)
    else:
        messages = UiMessages()
        messages.add_warning(_("The feedback you saved was not published and is therefore not visible to the student."))
        messages.save(request)
    
    return HttpResponseRedirect(
            reverse('devilry-examiner-show_assignmentgroup',
                args=(delivery_obj.assignment_group.id,)))

def render_response(request, delivery_obj, feedback_form, grade_form,
        template_path='devilry/examiner/correct_delivery.django.html'):
    return render_to_response(template_path, {
            'delivery': delivery_obj,
            'feedback_form': feedback_form,
            'grade_form': grade_form,
        }, context_instance=RequestContext(request))

def view_shortcut(request, delivery_obj, grade_model_cls, grade_form_cls):
    """
    Creates a feedback-view.

    :param delivery_obj:
        A :class:`devilry.core.models.Delivery` object.
    :param grade_model_cls:
        A subclass of class:`devilry.core.gradeplugin.GradeModel`.
    :param grade_form_cls:
        A ``django.forms.ModelForm`` for editing objects of
        ``grade_model_cls``.
    """
    feedback_form = parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.grade:
        grade_obj = feedback_obj.grade
    else:
        grade_obj = grade_model_cls()

    if request.method == 'POST':
        grade_form = grade_form_cls(request.POST, instance=grade_obj, prefix='grade')
    else:
        grade_form = grade_form_cls(instance=grade_obj, prefix='grade')

    if request.method == 'POST':
        if feedback_form.is_valid() and grade_form.is_valid():
            grade_form.save()
            feedback_form.instance.grade = grade_form.instance
            feedback_form.save()
            return redirect_after_successful_save(request, delivery_obj)

    return render_response(request, delivery_obj,
            feedback_form, grade_form)
