from os.path import basename

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from django.db import transaction
from django.utils.translation import ugettext as _

from devilry.ui.messages import UiMessages
from devilry.core.utils.GroupNodes import group_assignmentgroups
from devilry.core.models import Delivery, AssignmentGroup
from devilry.ui.defaults import DATETIME_FORMAT
from devilry.core.utils.verify_unique_entries import verify_unique_entries
from devilry.core.devilry_email import send_email


@login_required
@transaction.autocommit
def add_delivery(request, assignment_group_id, messages=None):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    if not assignment_group.is_candidate(request.user) or \
            not assignment_group.can_add_deliveries():
        return HttpResponseForbidden("Forbidden")

    if not messages:
        messages = UiMessages()

    valid_filenames = None
    upload_file_count = 10
    filenames_to_deliver = None

    if assignment_group.parentnode.filenames:
        filenames_to_deliver = assignment_group.parentnode.get_filenames()
        valid_filenames = {}
        for fname in filenames_to_deliver:
            valid_filenames[fname] = fname
        upload_file_count = len(valid_filenames)

    class UploadFileForm(forms.Form):
        file = forms.FileField()
    
        def __init__(self, *args, **kwargs):
            super(UploadFileForm, self).__init__(*args, **kwargs)

        def clean(self):
            f = super(UploadFileForm, self).clean()
            #if 'file' in f:
            #    filename = self.cleaned_data['file'].name
            #    if not valid_filenames.has_key(filename):
            #        raise forms.ValidationError("Incorrect filename %s" % filename)
            return f

    UploadFileFormSet = formset_factory(UploadFileForm, extra=upload_file_count)

    if request.method == 'POST':
        formset = UploadFileFormSet(request.POST, request.FILES)
        if formset.is_valid():
            if not verify_unique_entries(request.FILES.values()):
                messages.add_error(_("The filenames are not unique."))
            else:
                filenames_valid = True

                if len(request.FILES.values()) == 0:
                    messages.add_error(_("You must choose at least one file to deliver."))
                    filenames_valid = False
                    
                if filenames_valid:
                    delivery = Delivery.begin(assignment_group, request.user)
                    for f in request.FILES.values():
                        filename = basename(f.name) # do not think basename is needed, but at least we *know* we only get the filename.
                        delivery.add_file(filename, f.chunks())
                    delivery.finish()
                    return HttpResponseRedirect(
                        reverse('devilry-student-successful_delivery',
                                args=[assignment_group_id]))

    else:
        formset = UploadFileFormSet()

    return render_to_response('devilry/student/add_delivery.django.html', {
        'assignment_group': assignment_group,
        'formset': formset,
        'messages': messages,
        'filenames_to_deliver': filenames_to_deliver,
        }, context_instance=RequestContext(request))


def successful_delivery(request, assignment_group_id):
    messages = UiMessages()
    messages.add_info(_('Successful delivery'))
    
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    period = assignment_group.parentnode.parentnode
    subject = period.parentnode
    latest = assignment_group.deliveries.all()[0]
    
    email_message = _("This is a receipt for your delivery.")
    email_message += "\n\n"
    email_message += _("Time of delivery: %s\n") \
                     % latest.time_of_delivery.strftime(DATETIME_FORMAT)
    email_message += _("Subject: %s\n") % subject.long_name
    email_message += _("Period: %s\n") % period.long_name
    email_message += _("\nFiles:\n")

    for fm in latest.filemetas.all():
        email_message += " - %s (%d bytes)\n" % (fm.filename, fm.size)
        
    cands = assignment_group.candidates.all()
    user_list = []
    for cand in cands:
        user_list.append(cand.student)

    try:
        send_email(user_list, 
                   _("Receipt for delivery on %s") \
                   % (assignment_group.parentnode.get_path()), 
                   email_message)
    except Exception, e:
        email_list = "".join(["%s (%s), " % (u.username, u.email) for u in user_list])[:-2]
        messages.add_warning(_('An error occured when sending email to the following users: %s.' \
                               % email_list))
    
    return show_assignmentgroup(request, assignment_group_id, messages)


@login_required
def show_assignmentgroup(request, assignmentgroup_id, messages=None):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_candidate(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/student/show_assignmentgroup.django.html', {
        'assignment_group': assignment_group,
        'messages': messages,
        }, context_instance=RequestContext(request))

@login_required
def show_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_candidate(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/student/show_delivery.django.html', {
        'delivery': delivery,
        'assignment_group': delivery.assignment_group,
        }, context_instance=RequestContext(request))


@login_required
def list_assignments(request):
    assignment_groups = AssignmentGroup.active_where_is_candidate(request.user)
    old_assignment_groups = AssignmentGroup.old_where_is_candidate(request.user)

    if assignment_groups.count() == 0 \
            and old_assignment_groups.count() == 0:
        return HttpResponseForbidden("You are not a student")

    subjects = group_assignmentgroups(assignment_groups)
    old_subjects = group_assignmentgroups(old_assignment_groups)
    heading = _("Assignments")
    return render_to_response('devilry/student/list_assignments.django.html', {
            'subjects': subjects,
            'old_subjects': old_subjects,
            'has_subjects': len(subjects) > 0,
            'has_old_subjects': len(old_subjects) > 0,
            'page_heading': heading,
            }, context_instance=RequestContext(request))
