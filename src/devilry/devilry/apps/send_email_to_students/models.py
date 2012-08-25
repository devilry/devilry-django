from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import filesizeformat

from devilry.apps.core.models import StaticFeedback
from devilry.utils.devilry_email import send_email
from devilry_student.rest.add_delivery import successful_delivery_signal
from devilry.defaults.encoding import CHARSET


def create_absolute_show_delivery_url(delivery):
    url = reverse('devilry_student_show_delivery',
                      kwargs={'delivery_id': delivery.id})
    # See
    #   - https://code.djangoproject.com/ticket/16734
    #   - http://stackoverflow.com/questions/9814951/why-does-reverse-prepend-a-server-path
    #   - http://albertoconnor.ca/blog/2011/Sep/15/hosting-django-under-different-locations
    # for why reverse includes the full url
    #url = '{domain}{prefix}{path}'.format(domain = settings.DEVILRY_SCHEME_AND_DOMAIN,
                                          #prefix = settings.DEVILRY_URLPATH_PREFIX,
                                          #path = url)
    return url


def on_new_staticfeedback(sender, **kwargs):
    staticfeedback = kwargs['instance']
    delivery = staticfeedback.delivery
    deadline = delivery.deadline
    assignment_group = deadline.assignment_group
    assignment = assignment_group.parentnode
    period = assignment.parentnode
    subject = period.parentnode

    user_list = [candidate.student \
            for candidate in assignment_group.candidates.all()]

    url = create_absolute_show_delivery_url(delivery)
    email_subject = 'New feedback - {0}'.format(assignment.get_path())

    # Make sure the values that may contain non-ascii characters are utf-8
    unicode_kw = dict(subject = subject.long_name,
                      period = period.long_name,
                      assignment = assignment.long_name)
    for key, value in unicode_kw.iteritems():
        unicode_kw[key] = value.encode(CHARSET)

    email_message = ('One of your deliveries has new feedback.\n\n'
                     'Subject: {subject}\n'
                     'Period: {period}\n'
                     'Assignment: {assignment}\n'
                     'Deadline: {deadline}\n'
                     'Delivery number: {delivery}\n\n'
                     'The feedback can be viewed at:\n'
                     '{url}'.format(deadline = deadline.deadline.isoformat(),
                                    delivery = delivery.number,
                                    url = url,
                                    **unicode_kw))
    send_email(user_list, email_subject, email_message)

post_save.connect(on_new_staticfeedback,
                  sender=StaticFeedback, dispatch_uid='send_email_to_students_new_staticfeedback')



def on_new_successful_delivery(sender, delivery, **kwargs):
    deadline = delivery.deadline
    assignment_group = deadline.assignment_group
    assignment = assignment_group.parentnode
    period = assignment.parentnode
    subject = period.parentnode
    user_list = [candidate.student \
            for candidate in assignment_group.candidates.all()]
    url = create_absolute_show_delivery_url(delivery)

    files = ''
    for fm in delivery.filemetas.all():
        files += ' - {0} ({1})\n'.format(fm.filename, filesizeformat(fm.size))

    email_subject = 'Receipt for delivery on {0}'.format(assignment.get_path())
    email_message = ('This is a receipt for your delivery.\n\n'
                     'Subject: {subject}\n'
                     'Period: {period}\n'
                     'Assignment: {assignment}\n'
                     'Deadline: {deadline}\n'
                     'Delivery number: {deliverynumer}\n'
                     'Time of delivery: {time_of_delivery}\n'
                     'Files:\n{files}\n\n'
                     'The delivery can be viewed at:\n'
                     '{url}'.format(subject = subject.long_name,
                                    period = period.long_name,
                                    assignment = assignment.long_name,
                                    deadline = deadline.deadline.isoformat(),
                                    deliverynumer = delivery.number,
                                    time_of_delivery = delivery.time_of_delivery.isoformat(),
                                    files = files,
                                    url = url))
    send_email(user_list, email_subject, email_message)

successful_delivery_signal.connect(on_new_successful_delivery, dispatch_uid='send_email_to_students_new_delivery')
