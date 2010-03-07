from os.path import basename
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from devilry.core.models import (Delivery, AssignmentGroup,
        Node, Subject, Period, Assignment, FileMeta)
from devilry.core.widgets import ReadOnlyWidget
from django.db import transaction




@login_required
def list_assignmentgroups(request):
    return render_to_response('devilry/studentview/list_assignmentgroups.django.html', {
        'assignment_groups': AssignmentGroup.where_is_student(request.user),
        }, context_instance=RequestContext(request))

@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/show_assignmentgroup.django.html', {
        'assignment_group': assignment_group,
        }, context_instance=RequestContext(request))


@login_required
def list_deliveries(request):
    return render_to_response('devilry/studentview/list_deliveries.django.html', {
        'deliveries': Delivery.where_is_student(request.user),
        }, context_instance=RequestContext(request))

@login_required
def show_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/show_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))


class UploadFileForm(forms.Form):
    file = forms.FileField()
UploadFileFormSet = formset_factory(UploadFileForm, extra=10)



@login_required
@transaction.autocommit
def add_delivery(request, assignment_group_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    if not assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    if request.method == 'POST':
        formset = UploadFileFormSet(request.POST, request.FILES)
        if formset.is_valid():
            delivery = Delivery.begin(assignment_group, request.user)
            for f in request.FILES.values():
                filename = basename(f.name) # do not think basename is needed, but at least we *know* we only get the filename.
                delivery.add_file(filename, f.chunks())
            delivery.finish()
            return HttpResponseRedirect(reverse('devilry.studentview.views.successful_delivery', args=(delivery.id,)))
    else:
        formset = UploadFileFormSet()

    return render_to_response('devilry/studentview/add_delivery.django.html', {
        'assignment_group': assignment_group,
        'formset': formset,
        }, context_instance=RequestContext(request))


@login_required
def successful_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/successful_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))


@login_required
def main(request):
    
    assignment_groups = AssignmentGroup.where_is_student(request.user)
        
    dict = {}

    for group in assignment_groups:
        
        if not dict.has_key(group.parentnode.parentnode.str()):
            dict[group.parentnode.parentnode.str()] = Course()

        dict[group.parentnode.parentnode.str()].add_course(group)
    

    return render_to_response('devilry/studentview/main.django.html', {
            'assignment_groups': assignment_groups,
            'courses': dict.values(),
            }, context_instance=RequestContext(request))


class Course(object):

    def __init__(self):
        self.assignment_groups = list()
    
    def add_course(self, assignment_group):
        self.assignment_groups.append(assignment_group)

    def assignment_groups(self):
        self.assignment_groups.iter()
