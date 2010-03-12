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


class EditNodeBase(object):
    VIEW_NAME = None
    MODEL_CLASS = None

    def __init__(self, request, node_id):
        self.request = request

        if node_id == None:
            self.node = self.MODEL_CLASS()
        else:
            self.node = get_object_or_404(self.MODEL_CLASS, pk=node_id)
        if not self.node.can_save(request.user):
            return HttpResponseForbidden("Forbidden")

        if self.node.pk == None:
            self.post_url = reverse('add-' + self.VIEW_NAME)
        else:
            self.post_url = reverse('edit-' + self.VIEW_NAME, args=(str(self.node.pk)))


    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = self.MODEL_CLASS.where_is_admin(self.request.user))
            class Meta:
                model = self.MODEL_CLASS
        return NodeForm


    def create_view(self):
        model_name = self.MODEL_CLASS._meta.verbose_name
        form_cls = self.create_form()
        message = None
        if self.request.POST:
            nodeform = form_cls(self.request.POST, instance=self.node)
            if nodeform.is_valid():
                nodeform.save()
                message = model_name + ' saved'
        else:
            nodeform = form_cls(instance=self.node)

        d = {'model_name': model_name}
        if self.node.id == None:
            title = _('New %(model_name)s') % d
        else:
            title = _('Edit %(model_name)s' % d)

        return render_to_response('devilry/adminview/edit_node.django.html', {
            'title': title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': nodeform,
            'message': message,
            'post_url': self.post_url,
            }, context_instance=RequestContext(self.request))


class EditNode(EditNodeBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin(self.request.user))
            class Meta:
                model = Node
        return NodeForm

class EditSubject(EditNodeBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

class EditPeriod(EditNodeBase):
    VIEW_NAME = 'period'
    MODEL_CLASS = Period

class EditAssignment(EditNodeBase):
    VIEW_NAME = 'assignment'
    MODEL_CLASS = Assignment


@login_required
def edit_node(request, node_id=None):
    return EditNode(request, node_id).create_view()


@login_required
def edit_subject(request, node_id=None):
    return EditSubject(request, node_id).create_view()

@login_required
def edit_period(request, node_id=None):
    return EditPeriod(request, node_id).create_view()

@login_required
def edit_assignment(request, node_id=None):
    return EditAssignment(request, node_id).create_view()




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
