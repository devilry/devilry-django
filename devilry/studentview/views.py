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
from django.contrib.auth import authenticate, login, logout
from devilry.core.widgets import ReadOnlyWidget



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('admin'))


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def login_view(request):
    login_failed = False
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('admin'))
                else:
                    return HttpResponseForbidden("Acount is not active")
            else:
                login_failed = True
    else:
        form = LoginForm()
    return render_to_response('devilry/studentview/login.django.html', {
        'form': form,
        'login_failed': login_failed,
        }, context_instance=RequestContext(request))




@login_required
def admin(request):
    return render_to_response('devilry/studentview/admin.django.html', {
        'nodes': Node.where_is_admin(request.user),
        'subjects': Subject.where_is_admin(request.user),
        'periods': Period.where_is_admin(request.user),
        'assignments': Assignment.where_is_admin(request.user),
        }, context_instance=RequestContext(request))



def edit_node_generic(request, nodecls, parentnodecls, view_name, node_id=None):
    class NodeForm(forms.ModelForm):
        parentnode = forms.ModelChoiceField(
                queryset = parentnodecls.where_is_admin(request.user),
                empty_label = "(Nothing)")
        class Meta:
            model = nodecls

    message = None
    if node_id == None:
        if not request.user.is_superuser:
            if nodecls == Node:
                return HttpResponseForbidden("Forbidden")
            elif parentnodecls.where_is_admin(request.user).count() == 0:
                return HttpResponseForbidden("Forbidden")
        node = nodecls()
        post_url = reverse('add-' + view_name)
    else:
        node = get_object_or_404(nodecls, pk=node_id)
        if not node.is_admin(request.user):
            return HttpResponseForbidden("Forbidden")
        post_url = reverse('edit-' + view_name, args=(str(node.pk)))

    if request.POST:
        nodeform = NodeForm(request.POST, instance=node)
        if nodeform.is_valid():
            nodeform.save()
            message = nodecls._meta.verbose_name + ' saved'
    else:
        nodeform = NodeForm(instance=node)
    return render_to_response('devilry/studentview/edit_node.django.html', {
        'nodeform': nodeform,
        'message': message,
        'post_url': post_url,
        }, context_instance=RequestContext(request))

@login_required
def edit_node(request, node_id=None):
    return edit_node_generic(request, Node, Node, 'node', node_id)

@login_required
def edit_subject(request, node_id=None):
    return edit_node_generic(request, Subject, Node, 'subject', node_id)

@login_required
def edit_period(request, node_id=None):
    return edit_node_generic(request, Period, Subject, 'period', node_id)

@login_required
def edit_assignment(request, node_id=None):
    return edit_node_generic(request, Assignment, Period, 'assignment', node_id)




def list_nodes_generic(request, nodecls):
    return render_to_response('devilry/studentview/list_nodes.django.html', {
        'nodes': nodecls.where_is_admin(request.user),
        }, context_instance=RequestContext(request))

@login_required
def list_nodes(request):
    return list_nodes_generic(request, Node)

@login_required
def list_subjects(request):
    return list_nodes_generic(request, Subject)

@login_required
def list_periods(request):
    return list_nodes_generic(request, Period)

@login_required
def list_assignments(request):
    return list_nodes_generic(request, Assignment)


@login_required
def list_assignmentgroups(request):
    return render_to_response('devilry/studentview/list_assignmentgroups.django.html', {
        'assignment_groups': AssignmentGroup.where_is_student(request.user),
        }, context_instance=RequestContext(request))

@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignmentgroup = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignmentgroup.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response('devilry/studentview/show_assignmentgroup.django.html', {
        'assignmentgroup': assignmentgroup,
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
def add_delivery(request, assignment_group_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignment_group_id)
    if not assignment_group.is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    if request.method == 'POST':
        formset = UploadFileFormSet(request.POST, request.FILES)
        if formset.is_valid():
            delivery = Delivery.begin(assignment_group)
            for f in request.FILES.values():
                filename = basename(f.name) # do not think basename is needed, but at least we *know* we only get the filename.
                FileMeta.create(delivery, filename, f.chunks())
            delivery.finish()
            return HttpResponseRedirect(reverse('successful-delivery', args=(delivery.id,)))
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
    return render_to_response('devilry/studentview/main.django.html',
            context_instance=RequestContext(request))

