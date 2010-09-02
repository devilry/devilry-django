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
from devilry.core.utils.GroupNodes import group_assignmentgroups, print_tree
from devilry.core.models import Delivery, AssignmentGroup
from devilry.ui.defaults import DATETIME_FORMAT
from devilry.core.utils.verify_unique_entries import verify_unique_entries
from devilry.core.devilry_email import send_email



class UploadFileForm(forms.Form):
        file = forms.FileField()

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
        valid_filenames = assignment_group.parentnode.get_filenames() 
        upload_file_count = len(valid_filenames)
        filenames_to_deliver = ''.join([f + ", " for f in valid_filenames])
        filenames_to_deliver = filenames_to_deliver[:-2]

    UploadFileFormSet = formset_factory(UploadFileForm, extra=upload_file_count)

    if request.method == 'POST':
        formset = UploadFileFormSet(request.POST, request.FILES)
        if formset.is_valid():
            if not verify_unique_entries(request.FILES.values()):
                messages.add_error(_("The filenames are not unique."))
            else:
                filenames_valid = True
                if assignment_group.parentnode.filenames:
                    filenames = []
                    for i in range(0, formset.total_form_count()):
                        form = formset.forms[i]
                        
                        if 'file' in form.cleaned_data:
                            filename = form.cleaned_data['file']
                            if filename != '':
                                filenames.append(filename)
                    try:
                        assignment_group.parentnode.validate_filenames(filenames)
                                                
                        if len(filenames) == 0:
                            messages.add_error(_("You must choose at least one file to deliver."))
                            filenames_valid = False

                    except ValueError, e:
                        filenames_valid = False
                        messages.add_error(_("%s" % e))

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
    
    email_message = "This is a receipt for your delivery."
    email_message += "\n\n"
    email_message += "Subject: %s - %s\n" % (subject.long_name, period.long_name)
    email_message += "Time of delivery: %s\n" % latest.time_of_delivery.strftime(DATETIME_FORMAT)
    email_message += "Files:\n"

    for fm in latest.filemetas.all():
        email_message += " - %s (%d bytes)\n" % (fm.filename, fm.size)
        
    cands = assignment_group.candidates.all()
    user_list = []
    for cand in cands:
        user_list.append(cand.student)
    
    send_email(user_list, 
                    "Receipt for your delivery on %s" % (subject.short_name), 
                    email_message)
    
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
        }, context_instance=RequestContext(request))
