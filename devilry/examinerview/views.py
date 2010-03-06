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
def list_assignments(request):
    #assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignments = Assignment.where_is_examiner(request.user)

    if assignments.count() == 0:
        return HttpResponseForbidden("You are not registered as examiner on any assignments.")
    return render_to_response('devilry/examinerview/show_assignments.django.html', {
        'assignments': assignments,
        }, context_instance=RequestContext(request))


@login_required
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(request.user)
    
    return render_to_response('devilry/examinerview/list_assignmentgroups.django.html', {
        'assignment_groups': assignment_groups,
        }, context_instance=RequestContext(request))

"""
@login_required
def list_assignmentgroups(request):
    return render_to_response('devilry/examinerview/list_assignmentgroups.django.html', {
        'assignment_groups': AssignmentGroup.where_is_student(request.user),
        }, context_instance=RequestContext(request))
"""




@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/examinerview/show_assignmentgroup.django.html', {
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
    return render_to_response('devilry/examinerview/show_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))


class UploadFileForm(forms.Form):
    file = forms.FileField()
UploadFileFormSet = formset_factory(UploadFileForm, extra=10)


class CorrectForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ('grade', 'feedback', 'feedback_format')



@login_required
@transaction.autocommit
def correct_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)

    if not delivery.assignment_group.is_examiner(request.user):
        print "forbidden"
        return HttpResponseForbidden("Forbidden")
    
    if request.method == 'POST':
        form = CorrectForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            #return HttpResponseRedirect(reverse('successful-delivery', args=(delivery.id,)))
    else:
        form = CorrectForm(instance=delivery)

    return render_to_response('devilry/examinerview/correct_delivery.django.html', {
        'delivery': delivery,
        'assignment_group': delivery.assignment_group,
        'text_format': delivery.feedback_format,
        'form': form,
        }, context_instance=RequestContext(request))




@login_required
def successful_delivery(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery.assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/examinerview/successful_delivery.django.html', {
        'delivery': delivery,
        }, context_instance=RequestContext(request))


@login_required
def main(request):
    assignment_pks = AssignmentGroup.where_is_examiner(request.user).values("parentnode").distinct().query
    assignments = Assignment.objects.filter(pk__in=assignment_pks)
    return render_to_response('devilry/examinerview/main.django.html', {
            'assignments': assignments,
            }, context_instance=RequestContext(request))


from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper


@login_required
def download_file(request, filemeta_id):
    filemeta = get_object_or_404(FileMeta, pk=filemeta_id)
    response = HttpResponse(FileWrapper(
            file(filemeta.store._get_filepath(filemeta))), content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=" + filemeta.filename
    response['Content-Length'] = filemeta.size

    return response

