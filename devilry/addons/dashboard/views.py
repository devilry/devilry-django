from os.path import basename
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from devilry.core.models import (Delivery, Feedback, AssignmentGroup,
        Node, Subject, Period, Assignment, FileMeta)

import dashboardplugin_registry
from django.db import transaction



@login_required
def correct_delivery(request, delivery_id):
    delivery_obj = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery_obj.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    key = delivery_obj.assignment_group.parentnode.grade_plugin
    return gradeplugin_registry.get(key).view(request, delivery_obj)


@login_required
def successful_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/examinerview/successful_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))


from devilry.core.utils.GroupAssignments import group_assignments 


@login_required
def main(request):
    
    is_student = AssignmentGroup.where_is_student(request.user).count() > 0
    is_examiner = AssignmentGroup.where_is_examiner(request.user).count() > 0
    is_admin = Assignment.where_is_admin(request.user).count() > 0

    values_iterator = dashboardplugin_registry.iter_values(student=is_student, examiner=is_examiner, admin=is_admin)
                                  
    return render_to_response('devilry/dashboard/main.django.html', {
            'applications': values_iterator,
            }, context_instance=RequestContext(request))
