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
from devilry.ui.messages import UiMessages
from devilry.core import gradeplugin_registry
from devilry.ui.widgets import DevilryDateTimeWidget, DevilryMultiSelectFew
from devilry.ui.fields import MultiSelectCharField


@login_required
def main(request):
    return render_to_response('devilry/admin/main.django.html', {
        'nodes': Node.where_is_admin(request.user),
        'subjects': Subject.where_is_admin(request.user),
        'periods': Period.where_is_admin(request.user),
        'assignments': Assignment.where_is_admin(request.user),
        }, context_instance=RequestContext(request))


class EditNodeBase(object):
    VIEW_NAME = None
    MODEL_CLASS = None

    def __init__(self, request, node_id, successful_save=True):
        self.request = request
        self.messages = UiMessages()
        if successful_save:
            self.messages.add_success(_('Save successful'))
        self.parent_model = self.MODEL_CLASS.parentnode.field.related.parent_model

        if node_id == None:
            self.is_new = True
            self.node = self.MODEL_CLASS()
        else:
            self.is_new = False
            self.node = get_object_or_404(self.MODEL_CLASS, pk=node_id)

        if self.is_new:
            self.post_url = self.get_reverse_url()
        else:
            self.post_url = self.get_reverse_url(str(self.node.pk))

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = self.parent_model.where_is_admin(self.request.user))
            class Meta:
                model = self.MODEL_CLASS
        return NodeForm


    def get_reverse_url(self, *args):
        return reverse(__name__ + '.edit_' + self.VIEW_NAME, args=args)


    def create_view(self):
        if not self.node.can_save(self.request.user):
            return HttpResponseForbidden("Forbidden")

        model_name = self.MODEL_CLASS._meta.verbose_name
        model_name_dict = {'model_name': model_name}
        form_cls = self.create_form()

        if self.request.POST:
            nodeform = form_cls(self.request.POST, instance=self.node)
            if nodeform.is_valid():
                nodeform.save()
                success_url = self.get_reverse_url(str(self.node.pk))
                return HttpResponseRedirect(success_url)
        else:
            nodeform = form_cls(instance=self.node)

        if self.node.id == None:
            title = _('New %(model_name)s') % model_name_dict
        else:
            title = _('Edit %(model_name)s' % model_name_dict)

        return render_to_response('devilry/admin/edit_node.django.html', {
            'title': title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': nodeform,
            'messages': self.messages,
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

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Subject.where_is_admin(self.request.user))
            class Meta:
                model = Period
                fields = ['parentnode', 'short_name', 'long_name', 'start_time', 'end_time', 'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                }
        return Form



class EditAssignment(EditNodeBase):
    VIEW_NAME = 'assignment'
    MODEL_CLASS = Assignment
    
    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Period.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew)
            
            class Meta:
                model = Assignment
                fields = ['parentnode', 'short_name', 'long_name', 'publishing_time', 'deadline', 'admins']
                if self.is_new:
                    fields.append('grade_plugin')
                widgets = {
                    'publishing_time': DevilryDateTimeWidget,
                    'deadline': DevilryDateTimeWidget,
                    'admins': DevilryMultiSelectFew,
                }
        return Form

    def create_view(self):
        if not self.is_new:
            gradeplugin = gradeplugin_registry.get(self.node.grade_plugin)
            msg = _('This assignment uses the <em>%(gradeplugin_label)s</em> ' \
                    'grade-plugin. You cannot change grade-plugin on an ' \
                    'existing assignment.' % {'gradeplugin_label': gradeplugin.label})
            if gradeplugin.admin_url_callback:
                url = gradeplugin.admin_url_callback(self.node.id)
                msg2 = _('<a href="%(gradeplugin_admin_url)s">Click here</a> '\
                        'to administer the plugin.' % {'gradeplugin_admin_url': url})
                self.messages.add_info('%s %s' % (msg, msg2), raw_html=True)
            else:
                self.messages.add_info(msg, raw_html=True)
        return super(EditAssignment, self).create_view()


@login_required
def edit_node(request, node_id=None, successful_save=False):
    return EditNode(request, node_id, successful_save).create_view()


@login_required
def edit_subject(request, node_id=None, successful_save=False):
    return EditSubject(request, node_id, successful_save).create_view()

@login_required
def edit_period(request, node_id=None, successful_save=False):
    return EditPeriod(request, node_id, successful_save).create_view()

@login_required
def edit_assignment(request, node_id=None, successful_save=False):
    return EditAssignment(request, node_id, successful_save).create_view()




def list_nodes_generic(request, nodecls):
    return render_to_response('devilry/admin/list_nodes.django.html', {
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
