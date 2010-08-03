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



class UploadFileForm(forms.Form):
    file = forms.FileField()
UploadFileFormSet = formset_factory(UploadFileForm, extra=10)


@login_required
def add_delivery_choose_assignment(request):
    active_assignment_groups = AssignmentGroup.active_where_is_candidate(request.user)
    subjects = group_assignmentgroups(active_assignment_groups)

    return render_to_response('devilry/student/add_delivery_choose_assignment.django.html', {
            'subjects': subjects,
            'urlname': 'devilry-student-add_delivery',
            }, context_instance=RequestContext(request))


@login_required
@transaction.autocommit
def add_delivery(request, assignment_group_id, messages=None):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    if not assignment_group.is_candidate(request.user):
        return HttpResponseForbidden("Forbidden")
    if request.method == 'POST':
        formset = UploadFileFormSet(request.POST, request.FILES)
        if formset.is_valid():
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
        }, context_instance=RequestContext(request))


def successful_delivery(request, assignment_group_id):
    messages = UiMessages()
    messages.add_info(_('Successful delivery'))
    return add_delivery(request, assignment_group_id, messages)


@login_required
def show_assignments(request):
    assignment_groups = AssignmentGroup.active_where_is_candidate(request.user)
    subjects = group_assignmentgroups(assignment_groups)
    old_assignment_groups = AssignmentGroup.old_where_is_candidate(request.user)
    old_subjects = group_assignmentgroups(old_assignment_groups)
    return render_to_response('devilry/student/show-assignments.django.html', {
            'subjects': subjects,
            'old_subjects': old_subjects,
            }, context_instance=RequestContext(request))

@login_required
def show_history(request):
    old_assignment_groups = AssignmentGroup.published_where_is_candidate(request.user)
    subjects = group_assignmentgroups(old_assignment_groups)

    return render_to_response('devilry/student/show-history.django.html', {
            'subjects': subjects,
            }, context_instance=RequestContext(request))

@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_candidate(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/student/show_assignmentgroup.django.html', {
        'assignment_group': assignment_group,
        }, context_instance=RequestContext(request))

@login_required
def show_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_candidate(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/student/show_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))
