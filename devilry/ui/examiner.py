from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.core.models import AssignmentGroup
from devilry.core.devilry_email import (
        send_email, NoEmailAddressException,
        SMTPException)


def send_feedback_email(request, messages, delivery_obj):
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
    email_list = ", ".join(["%s (%s)" % (u.username, u.email) for u in user_list])[:-2]
    try:
        send_email(user_list, 
                   _("New feedback - %s") % (assignment.get_path()), 
                   email_message)
    except SMTPException, e:
        messages.add_warning(str(e))
    except NoEmailAddressException, e:
        messages.add_warning(str(e))
    else:
        messages.add_info(
                _("Published feedback notification mail sent to: "
                    "%(email_list)s") % dict(email_list=email_list))


def publish_feedback_react(request, messages, delivery_obj):
    # Read the group from database, to avoid overwriting status and
    # other cached fields updated by signal handlers
    group = AssignmentGroup.objects.get(id=delivery_obj.assignment_group.id)
    attempts = group.deliveries.filter(feedback__published=True).count()
    maxattempts = group.parentnode.attempts
    if delivery_obj.feedback.get_grade().is_passing_grade():
        messages.add_info(
                "Because you saved and published feedback "
                "with passing grade.",
                title="Group automatically closed")
        group.is_open = False
        group.save()
    elif maxattempts and attempts >= maxattempts and group.is_open:
        messages.add_info(
                "The group was automatically closed for more "
                "deliveries because the student has failed to get a "
                "passing grade %(maxattempts)s or more times." % dict(
                    maxattempts=maxattempts))
        group.is_open = False
        group.save()
    else:
        messages.add_info(_("%(group)s published successfully") %
                dict(group=str(group)))


def post_publish_feedback(request, messages, delivery_obj):
    publish_feedback_react(request, messages, delivery_obj)
    send_feedback_email(request, messages, delivery_obj)
