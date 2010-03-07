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
        
    courses = group_assignments(assignment_groups)

    print courses

    return render_to_response('devilry/studentview/main.django.html', {
            'assignment_groups': assignment_groups,
            'courses': courses,
            }, context_instance=RequestContext(request))


def group_assignments(assignment_groups):
    
    dict = OrderedDict()

    for group in assignment_groups:
        
        if not dict.has_key(group.parentnode.parentnode.parentnode):
            subject = Subject(group.parentnode.parentnode.parentnode.short_name)
            dict[group.parentnode.parentnode.parentnode] = subject

        dict[group.parentnode.parentnode.parentnode].add_period(group)

    return dict.values()


from devilry.core.utils import OrderedDict

class Subject(object):

    def __init__(self, name):
        self.periods = OrderedDict()
        self.name = name
            
    def __str__(self):
        return self.name

    def add_period(self, assignment_group):
        
        if not self.periods.has_key(assignment_group.parentnode.parentnode):
            period = Period(assignment_group.parentnode.parentnode.short_name)
            self.periods[assignment_group.parentnode.parentnode] = period

        self.periods[assignment_group.parentnode.parentnode].add_assignment(assignment_group)

    def __iter__(self):
        return iter(self.periods.values())


class Period(object):

    def __init__(self, name):
        self.assignments = list()
        self.name = name
    
    def __str__(self):
        return self.name

    def add_assignment(self, assignment_group):
        self.assignments.append(assignment_group)

    def __iter__(self):
        return iter(self.assignments)
