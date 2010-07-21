from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory

from devilry.core.models import Node, Period, Assignment, AssignmentGroup, \
        Deadline, Subject
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
        'assignmentgroups': AssignmentGroup.where_is_admin(request.user),
        }, context_instance=RequestContext(request))


class EditBase(object):
    VIEW_NAME = None
    MODEL_CLASS = None

    def __init__(self, request, obj_id, successful_save=True):
        self.request = request
        self.messages = UiMessages()
        if successful_save:
            self.messages.add_success(_('Save successful'))
        self.parent_model = self.MODEL_CLASS.parentnode.field.related.parent_model

        if obj_id == None:
            self.is_new = True
            self.obj = self.MODEL_CLASS()
        else:
            self.is_new = False
            self.obj = get_object_or_404(self.MODEL_CLASS, pk=obj_id)

        if self.is_new:
            self.post_url = self.get_reverse_url()
        else:
            self.post_url = self.get_reverse_url(str(self.obj.pk))

    def create_form(self):
        raise NotImplementedError, "create_form must be implemented"
    
    def get_reverse_url(self, *args):
        return reverse(__name__ + '.edit_' + self.VIEW_NAME, args=args)
    
    """
    def create_view(self):
        if not self.obj.can_save(self.request.user):
            return HttpResponseForbidden("Forbidden")

        model_name = self.MODEL_CLASS._meta.verbose_name
        model_name_dict = {'model_name': model_name}
        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            if objform.is_valid():
                objform.save()
                success_url = self.get_reverse_url(str(self.obj.pk))
                return HttpResponseRedirect(success_url)
        else:
            objform = form_cls(instance=self.obj)

        if self.obj.id == None:
            self.title = _('New %(model_name)s') % model_name_dict
        else:
            self.title = _('Edit %(model_name)s' % model_name_dict)

        return render_to_response('devilry/admin/edit_node.django.html', {
            'title': self.title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': objform,
            'messages': self.messages,
            'post_url': self.post_url,
            }, context_instance=RequestContext(self.request))
            """

    def make_view(self):
        if not self.obj.can_save(self.request.user):
            return HttpResponseForbidden("Forbidden")

        model_name = self.MODEL_CLASS._meta.verbose_name
        model_name_dict = {'model_name': model_name}
        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            if objform.is_valid():
                objform.save()
                success_url = self.get_reverse_url(str(self.obj.pk))
                return HttpResponseRedirect(success_url)
        else:
            objform = form_cls(instance=self.obj)

        if self.obj.id == None:
            self.title = _('New %(model_name)s') % model_name_dict
        else:
            self.title = _('Edit %(model_name)s' % model_name_dict)

        return {
            'title': self.title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': objform,
            'messages': self.messages,
            'post_url': self.post_url,
            }
    
    def create_view(self):
        return render_to_response('devilry/admin/edit_node.django.html', 
                                  self.make_view(), 
                                  context_instance=RequestContext(self.request))


class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin(self.request.user))
            class Meta:
                model = Node
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
                widgets = {
                    'admins': DevilryMultiSelectFew,
                }
        return NodeForm

class EditSubject(EditBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = self.parent_model.where_is_admin(self.request.user))
            class Meta:
                model = self.MODEL_CLASS
        return NodeForm

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Node.where_is_admin(self.request.user))
            class Meta:
                model = Subject
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
                widgets = {
                    'admins': DevilryMultiSelectFew,
                }
        return Form

class EditPeriod(EditBase):
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
                    'admins': DevilryMultiSelectFew,
                }
        return Form

class EditAssignment(EditBase):
    VIEW_NAME = 'assignment'
    MODEL_CLASS = Assignment
    
    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Period.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew)
            
            class Meta:
                model = Assignment
                fields = ['parentnode', 'short_name', 'long_name', 'publishing_time', 'admins']
                if self.is_new:
                    fields.append('grade_plugin')
                widgets = {
                    'publishing_time': DevilryDateTimeWidget,
                    #'deadline': DevilryDateTimeWidget,
                    'admins': DevilryMultiSelectFew,
                }
        return Form

    def create_view(self):
        if not self.is_new:
            gradeplugin = gradeplugin_registry.getitem(self.obj.grade_plugin)
            msg = _('This assignment uses the <em>%(gradeplugin_label)s</em> ' \
                    'grade-plugin. You cannot change grade-plugin on an ' \
                    'existing assignment.' % {'gradeplugin_label': gradeplugin.label})
            if gradeplugin.admin_url_callback:
                url = gradeplugin.admin_url_callback(self.obj.id)
                msg2 = _('<a href="%(gradeplugin_admin_url)s">Click here</a> '\
                        'to administer the plugin.' % {'gradeplugin_admin_url': url})
                self.messages.add_info('%s %s' % (msg, msg2), raw_html=True)
            else:
                self.messages.add_info(msg, raw_html=True)
        return super(EditAssignment, self).create_view()


class EditAssignmentGroup(EditBase):
    VIEW_NAME = 'assignmentgroup'
    MODEL_CLASS = AssignmentGroup
    
    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Assignment.where_is_admin(self.request.user))
            #admins = MultiSelectCharField(widget=DevilryMultiSelectFew)
            
            DeadlineFormSet = inlineformset_factory(AssignmentGroup, Deadline)

            class Meta:
                model = AssignmentGroup
                fields = ['parentnode', 'name', 'candidates', 'examiners']
                widgets = {
                   # 'deadline': DevilryDateTimeWidget,
                    'examiners': DevilryMultiSelectFew,
                    'candidates': DevilryMultiSelectFew,
                }
        return Form

    def create_view(self):
        dic = self.make_view() 
        assignmentgroup = AssignmentGroup.objects.get(pk=self.obj.id)
        DeadlineFormSet = inlineformset_factory(AssignmentGroup, Deadline)

        if self.request.method == "POST":
            formset = DeadlineFormSet(request.POST, instance=assignmentgroup)
            if formset.is_valid():
                formset.save()
        else:
            formset = DeadlineFormSet(instance=assignmentgroup)

        dic['deadline_form'] = formset

        return render_to_response('devilry/admin/edit_assignmentgroup.django.html', 
                                  dic,
                                  context_instance=RequestContext(self.request))

@login_required
def edit_node(request, obj_id=None, successful_save=False):
    return EditNode(request, obj_id, successful_save).create_view()

@login_required
def edit_subject(request, obj_id=None, successful_save=False):
    return EditSubject(request, obj_id, successful_save).create_view()

@login_required
def edit_period(request, obj_id=None, successful_save=False):
    return EditPeriod(request, obj_id, successful_save).create_view()

@login_required
def edit_assignment(request, obj_id=None, successful_save=False):
    return EditAssignment(request, obj_id, successful_save).create_view()

@login_required
def edit_assignmentgroup(request, obj_id=None, successful_save=False):
    return EditAssignmentGroup(request, obj_id, successful_save).create_view()




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

@login_required
def list_assignmentgroups(request):
    return list_nodes_generic(request, AssignmentGroup)
