from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory, formset_factory

from devilry.core.models import Node, Period, Assignment, AssignmentGroup, \
        Deadline, Candidate, Subject
from devilry.ui.messages import UiMessages
from devilry.core import gradeplugin_registry
from devilry.ui.widgets import DevilryDateTimeWidget, DevilryMultiSelectFew
from devilry.ui.fields import MultiSelectCharField

from django.contrib.auth.models import User
import re

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
        
    def create_view(self):
        model_name = self.MODEL_CLASS._meta.verbose_name
        model_name_dict = {'model_name': model_name}
        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            if objform.is_valid():
                if not self.obj.can_save(self.request.user):
                    return HttpResponseForbidden("Forbidden")
                
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
  

class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew, 
                                          required=False)
            class Meta:
                model = Node
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
        return NodeForm

class EditSubject(EditBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Node.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew, 
                                          required=False)
            class Meta:
                model = Subject
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
        return Form

class EditPeriod(EditBase):
    VIEW_NAME = 'period'
    MODEL_CLASS = Period

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Subject.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew, 
                                          required=False)
            class Meta:
                model = Period
                fields = ['parentnode', 'short_name', 'long_name', 'start_time', 'end_time', 'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                    }
        return Form

class EditAssignment(EditBase):
    VIEW_NAME = 'assignment'
    MODEL_CLASS = Assignment
    
    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Period.not_ended_where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFew, 
                                          required=False)
            class Meta:
                model = Assignment
                fields = ['parentnode', 'short_name', 'long_name', 'publishing_time', 'admins']
                if self.is_new:
                    fields.append('grade_plugin')
                widgets = {
                    'publishing_time': DevilryDateTimeWidget,
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


class DeadlineForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=DevilryDateTimeWidget)
    text = forms.CharField(required=False,
            widget=forms.Textarea(attrs=dict(rows=5, cols=50)))
    class Meta:
        model = Deadline

class EditAssignmentGroup(EditBase):
    VIEW_NAME = 'assignmentgroup'
    MODEL_CLASS = AssignmentGroup
    
    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Assignment.where_is_admin(self.request.user))
            examiners = MultiSelectCharField(widget=DevilryMultiSelectFew,
                                             required=False)
                        
            class Meta:
                model = AssignmentGroup
                fields = ['parentnode', 'name', 'examiners', 'is_open']
                widgets = {
                    'examiners': DevilryMultiSelectFew,
                    }
        return Form

    def create_view(self):
        DeadlineFormSet = inlineformset_factory(AssignmentGroup, Deadline,
                extra=1, form=DeadlineForm)
        CandidatesFormSet = inlineformset_factory(AssignmentGroup,
                Candidate, extra=1)

        model_name = AssignmentGroup._meta.verbose_name
        model_name_dict = {'model_name': model_name}
        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            deadline_formset = DeadlineFormSet(self.request.POST,
                    instance=self.obj)
            candidates_formset = CandidatesFormSet(self.request.POST,
                    instance=self.obj)
            if objform.is_valid() \
                    and deadline_formset.is_valid() \
                    and candidates_formset.is_valid():
                if not self.obj.can_save(self.request.user):
                    return HttpResponseForbidden("Forbidden")
                objform.save()
                deadline_formset.save()
                candidates_formset.save()
                success_url = self.get_reverse_url(str(self.obj.pk))
                return HttpResponseRedirect(success_url)
        else:
            objform = form_cls(instance=self.obj)
            deadline_formset = DeadlineFormSet(instance=self.obj)
            candidates_formset = CandidatesFormSet(instance=self.obj)

        if self.obj.id == None:
            self.title = _('New %(model_name)s') % model_name_dict
        else:
            self.title = _('Edit %(model_name)s' % model_name_dict)

        return render_to_response(
                'devilry/admin/edit_assignmentgroup.django.html', {
                    'title': self.title,
                    'model_plural_name': AssignmentGroup._meta.verbose_name_plural,
                    'nodeform': objform,
                    'messages': self.messages,
                    'post_url': self.post_url,
                    'deadline_form': deadline_formset,
                    'candidates_form': candidates_formset
                }, context_instance=RequestContext(self.request))

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

class AssignmentgroupForm(forms.Form):
        name = forms.CharField()
        examiners = MultiSelectCharField(widget=DevilryMultiSelectFew,
                                       required=False)
        #examiners = forms.CharField()

class CreateAssignmentgroups:

        #@login_required
    def verify_assignmentgroups(self, request, assignment, initial_data):
        print "YES----------"

        AssignmentGroupsFormSet = formset_factory(AssignmentgroupForm)
        
        formset = None

        
        print "GET"
        data = {'form-TOTAL_FORMS': u'1',
                'form-INITIAL_FORMS': u'4',
                'form-MAX_NUM_FORMS': u'',
                }
         
        #print "inital data:", initial_data

        formset = AssignmentGroupsFormSet(initial=initial_data)
        
        #print "formset:", formset

        return render_to_response(
            'devilry/admin/verify_assignmentgroups.django.html', {
                'title': "Create assignmentsgroups",
                'formset': formset,
                'post_url': "save-assignmentgroups"
                }, context_instance=RequestContext(request))


    def save_assignmentgroups(self, request):
        print "Save assignmentgroups"
        if request.POST:
            AssignmentGroupsFormSet = formset_factory(AssignmentgroupForm)
            formset = AssignmentGroupsFormSet(request.POST)
            print "ass formset:", formset
        
        return HttpResponseRedirect("create-assignmentgroups")

@login_required
def save_assignmentgroups(request):
    return CreateAssignmentgroups().save_assignmentgroups(request)

@login_required
def create_assignmentgroups(request):

    class Form(forms.Form):
        parentnode = forms.ModelChoiceField(required=True,
                     queryset = Assignment.where_is_admin(request.user))
        assignment_groups = forms.CharField(widget=forms.widgets.Textarea())

    if request.POST:
        #print "post"
        form = Form(request.POST) 
        
        if form.is_valid():
            #print "valid"
            #print form.cleaned_data
            parentnode = form.cleaned_data['parentnode']
            groups = form.cleaned_data['assignment_groups']
        
            lines = groups.splitlines()

            initial_data = []
            
            for l in lines:
                if l.strip() == "":
                    continue
                m = re.match("(?:(?P<name>.+?)::)?(?P<users>.+)?", l)
                
                if not m:
                    continue
                
                group_data = {}

                name = m.group('name')
                users = m.group('users')

                print "name:", name
                print "users:", users

                if name:
                    group_data['name'] = name
                
                if users:
                    group_data['examiners'] = MultiSelectCharField.from_string(users)
                
                print "group data:", group_data

                initial_data.append(group_data)
                
            print "initial_data:", initial_data
            return CreateAssignmentgroups().verify_assignmentgroups(request, parentnode, initial_data)

        #return HttpResponseRedirect('/thanks/')
    else:
        print "GEt"
        form = Form()

    title = _('Create Assignment groups')
    messages = UiMessages()
    
    return render_to_response('devilry/admin/create_assignmentgroups.django.html', {
            'title': title,
            #'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': form,
            'messages': messages,
            #'post_url': self.get_reverse_url(),
            }, context_instance=RequestContext(request))




@login_required
def create_assignmentgroups1(request):

    class Form(forms.Form):
        parentnode = forms.ModelChoiceField(required=True,
                     queryset = Assignment.where_is_admin(request.user))
        assignment_groups = forms.CharField(widget=forms.widgets.Textarea())

    if request.POST:
        print "post"
        form = Form(request.POST) 
        
        if form.is_valid():
            print "valid"
            print form.cleaned_data
            parentnode = form.cleaned_data['parentnode']
            groups = form.cleaned_data['assignment_groups']
        
            lines = groups.splitlines()

            for l in lines:
                m = re.match("(?:(?P<name>.+?)::)?(?P<users>.+)?", l)
                
                if not m:
                    continue
                
                name = m.group('name')
                users = m.group('users')

                ag = AssignmentGroup()
                ag.parentnode = parentnode
                                
                if name:
                    ag.name = name
                
                ag.save()
    
                if users:
                    sep = re.compile(r',\s*')
                    usersplit = sep.split(users)
                        
                    for user in usersplit:
                        user_cand = user.split(':')
                        
                        try:
                            print "finding user:", user_cand[0]
                            userobj = User.objects.get(username=user_cand[0])
                            cand = Candidate()
                            cand.student = userobj
                            cand.assignment_group = ag

                            if len(user_cand) == 2 and user_cand[1].isdigit():
                                cand.candidate_id = user_cand[1]
                                                   
                            cand.save()
     
                            ag.candidates.add(cand)
                            ag.save()
                                                            
                        except Exception as e:
                            print e
                            print "user %s doesnt exist" % (user_cand)
        else:
            print "NOT VALID"
        
        #return HttpResponseRedirect('/thanks/')
    else:
        print "GEt"
        form = Form()

    title = _('Create Assignment groups')
    messages = UiMessages()
    
    return render_to_response('devilry/admin/create_assignmentgroups.django.html', {
            'title': title,
            #'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': form,
            'messages': messages,
            #'post_url': self.get_reverse_url(),
            }, context_instance=RequestContext(request))



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
