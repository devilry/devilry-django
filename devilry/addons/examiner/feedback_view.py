from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

from devilry.core.models import Feedback, AssignmentGroup
from devilry.ui.widgets import RstEditWidget
from devilry.ui.messages import UiMessages
from devilry.core.devilry_email import send_email
from devilry.core.utils.assignmentgroup import GroupDeliveriesByDeadline

from utils import get_next_notcorrected_in_assignment, \
        get_prev_notcorrected_in_assignment



class FeedbackForm(forms.ModelForm):
    """ A ModelForm for the :class:`devilry.core.models.Feedback`-class. """
    class Meta:
        model = Feedback
        fields = ('text', 'format', 'published')
        widgets = {
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
    messages = UiMessages()
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
        user_list = []
        for candidate in cands:
            user_list.append(candidate.student)

        rev = reverse('devilry-student-show-delivery', args=(delivery_obj.id,))
        email_message += _("\nThe feedback can be viewed at:\n%s\n") % \
                         (request.build_absolute_uri(rev))
        try:
            send_email(user_list, 
                       _("New feedback - %s") % (assignment.get_path()), 
                       email_message)
        except Exception, e:
            email_list = ", ".join(["%s (%s)" % (u.username, u.email) for u in user_list])[:-2]
            messages = UiMessages()
            messages.add_warning(_(
                'An error occured when sending email to the following '\
                'users: %s.' % email_list))
            messages.save(request)


        group = delivery_obj.assignment_group
        attempts = group.deliveries.filter(feedback__published=True).count()
        maxattempts = group.parentnode.attempts
        if delivery_obj.feedback.get_grade().is_passing_grade():
            messages.add_info(
                    "The group was automatically closed for more "
                    "deliveries because you saved and published feedback "
                    "with passing grade.")
            group.is_open = False
            group.save()
        elif attempts >= maxattempts and group.is_open:
            messages.add_info(
                    "The group was automatically closed for more "
                    "deliveries because the student has failed to get a "
                    "passing grade %(maxattempts)s or more times." % dict(
                        maxattempts=maxattempts))
            group.is_open = False
            group.save()
    else:
        messages.add_warning(_("The feedback was saved, but not published "
                "and is therefore not visible to the student."))

    messages.save(request)
    return HttpResponseRedirect(
            reverse('devilry-examiner-edit-feedback',
                args=(delivery_obj.id,)))


def render_response(request, delivery_obj, feedback_form, grade_form,
        template_path='devilry/examiner/edit_feedback.django.html',
        uimessages=None):
    """ Calls django.shortcuts.render_to_response with the given
    ``template_path`` and  ``delivery_obj``, ``feedback_form`` and
    ``grade_form`` as template variables. It also adds some template
    variables:
        
        after_deadline
            Boolean telling if the delivery is after the active deadline.
        diff_days
            Days between active deadline and delivery.
        diff_hours
            Hours between active deadline and delivery.
        diff_minutes
            Minutes between active deadline and delivery.
    """
    next_notcorrected = get_next_notcorrected_in_assignment(request.user,
            delivery_obj)
    prev_notcorrected = get_prev_notcorrected_in_assignment(request.user,
            delivery_obj)

    active_deadline = delivery_obj.assignment_group.get_active_deadline().deadline
    after_deadline = active_deadline < delivery_obj.time_of_delivery
    if after_deadline:
        diff = delivery_obj.time_of_delivery - active_deadline
    else:
        diff = active_deadline - delivery_obj.time_of_delivery
    days = diff.days
    m = diff.seconds/60
    hours = m/60
    minutes = m%60

    deliveries_by_deadline = GroupDeliveriesByDeadline(
            delivery_obj.assignment_group)

    show_deadline_hint = delivery_obj.assignment_group.is_open and \
        delivery_obj.assignment_group.status == AssignmentGroup.CORRECTED_AND_PUBLISHED

    if not uimessages:
        uimessages = UiMessages()
        uimessages.load(request)

    return render_to_response(template_path, {
            'deliveries_by_deadline': deliveries_by_deadline,
            'delivery': delivery_obj,
            'feedback_form': feedback_form,
            'grade_form': grade_form,
            'after_deadline': after_deadline,
            'diff_days': days,
            'diff_hours': hours,
            'diff_minutes': minutes,
            'show_deadline_hint':show_deadline_hint,
            'messages': uimessages,
            'next_notcorrected': next_notcorrected,
            'prev_notcorrected': prev_notcorrected
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
            grade_form.instance.save(feedback_form.instance)
            feedback_form.instance.grade = grade_form.instance
            feedback_form.save()
            return redirect_after_successful_save(request, delivery_obj)

    return render_response(request, delivery_obj,
            feedback_form, grade_form)
