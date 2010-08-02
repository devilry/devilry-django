from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

from devilry.core.models import Node, Subject, Period, Assignment, \
    AssignmentGroup
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb
from devilry.ui.fields import MultiSelectCharField

from shortcuts import EditBase, list_nodes_generic
from assignment import edit_assignment, list_assignments
from assignmentgroup import list_assignmentgroups, edit_assignmentgroup, \
        create_assignmentgroups, save_assignmentgroups


@login_required
def main(request):
    return render_to_response('devilry/admin/main.django.html', {
        'nodes': Node.where_is_admin(request.user),
        'subjects': Subject.where_is_admin(request.user),
        'periods': Period.where_is_admin(request.user),
        'assignments': Assignment.where_is_admin(request.user),
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



class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
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
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
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
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False)
            class Meta:
                model = Period
                fields = ['parentnode', 'short_name', 'long_name', 'start_time', 'end_time', 'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                    }
        return Form



@login_required
def edit_node(request, obj_id=None, successful_save=False):
    return EditNode(request, obj_id, successful_save).create_view()

@login_required
def edit_subject(request, obj_id=None, successful_save=False):
    return EditSubject(request, obj_id, successful_save).create_view()

@login_required
def edit_period(request, obj_id=None, successful_save=False):
    return EditPeriod(request, obj_id, successful_save).create_view()
