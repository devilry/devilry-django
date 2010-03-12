from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _
from devilry.core.models import (Delivery, AssignmentGroup,
        Node, Subject, Period, Assignment, FileMeta)



@login_required
def main(request):
    return render_to_response('devilry/adminview/main.django.html', {
        'nodes': Node.where_is_admin(request.user),
        'subjects': Subject.where_is_admin(request.user),
        'periods': Period.where_is_admin(request.user),
        'assignments': Assignment.where_is_admin(request.user),
        }, context_instance=RequestContext(request))



def edit_node_generic(request, nodecls, parentnodecls, view_name,
        form_cls, node_id=None):

    message = None
    if node_id == None:
        node = nodecls()
        post_url = reverse('add-' + view_name)
    else:
        node = get_object_or_404(nodecls, pk=node_id)
        post_url = reverse('edit-' + view_name, args=(str(node.pk)))

    if not node.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    if request.POST:
        nodeform = form_cls(request.POST, instance=node)
        if nodeform.is_valid():
            nodeform.save()
            message = nodecls._meta.verbose_name + ' saved'
    else:
        nodeform = form_cls(instance=node)

    d = {'model_name': nodecls._meta.verbose_name}
    if node_id:
        title = _('Edit %(model_name)s' % d)
    else:
        title = _('New %(model_name)s') % d

    return render_to_response('devilry/adminview/edit_node.django.html', {
        'title': title,
        'model_plural_name': nodecls._meta.verbose_name_plural,
        'nodeform': nodeform,
        'message': message,
        'post_url': post_url,
        }, context_instance=RequestContext(request))



@login_required
def edit_node(request, node_id=None):
    class NodeForm(forms.ModelForm):
        parentnode = forms.ModelChoiceField(required=False,
                queryset = Node.where_is_admin(request.user))
        class Meta:
            model = Node
    return edit_node_generic(request, Node, Node, 'node', NodeForm, node_id)

@login_required
def edit_subject(request, node_id=None):
    class SubjectForm(forms.ModelForm):
        parentnode = forms.ModelChoiceField(
                queryset = Node.where_is_admin(request.user))
        class Meta:
            model = Subject
    return edit_node_generic(request, Subject, Node, 'subject', SubjectForm,
            node_id)

@login_required
def edit_period(request, node_id=None):
    class PeriodForm(forms.ModelForm):
        parentnode = forms.ModelChoiceField(
                queryset = Subject.where_is_admin(request.user))
        class Meta:
            model = Period
    return edit_node_generic(request, Period, Subject, 'period', PeriodForm,
            node_id)

@login_required
def edit_assignment(request, node_id=None):
    class AssignmentForm(forms.ModelForm):
        parentnode = forms.ModelChoiceField(
                queryset = Period.where_is_admin(request.user))
        class Meta:
            model = Assignment
    return edit_node_generic(request, Assignment, Period, 'assignment',
            AssignmentForm, node_id)




def list_nodes_generic(request, nodecls):
    return render_to_response('devilry/adminview/list_nodes.django.html', {
        'model_plural_name': nodecls._meta.verbose_name_plural,
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
