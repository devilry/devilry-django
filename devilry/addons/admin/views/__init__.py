from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _

from devilry.core.models import Node, Subject, Period, Assignment, \
        AssignmentGroup
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryLongNameWidget
from devilry.ui.fields import MultiSelectCharField

from shortcuts import EditBase, deletemany_generic, admins_help_text
from assignment import edit_assignment



@login_required
def edit_node(request, node_id=None):
    return EditNode(request, node_id).create_view()

@login_required
def edit_subject(request, subject_id=None):
    return EditSubject(request, subject_id).create_view()

@login_required
def edit_period(request, period_id=None):
    return EditPeriod(request, period_id).create_view()


@login_required
def delete_manynodes(request):
    return deletemany_generic(request, Node)

@login_required
def delete_manysubjects(request):
    return deletemany_generic(request, Subject)

@login_required
def delete_manyperiods(request):
    return deletemany_generic(request, Period)

@login_required
def delete_manyassignments(request):
    return deletemany_generic(request, Assignment)

@login_required
def delete_manyassignmentgroups(request, assignment_id):
    return deletemany_generic(request, AssignmentGroup,
            successurl=reverse('devilry-admin-edit_assignment',
                args=[assignment_id]))


class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin_or_superadmin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False,
                                          help_text=admins_help_text)
            class Meta:
                model = Node
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
                widgets = {'long_name': DevilryLongNameWidget}
        return NodeForm


class EditSubject(EditBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Node.where_is_admin_or_superadmin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False,
                                          help_text=admins_help_text)
            class Meta:
                model = Subject
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
                widgets = {'long_name': DevilryLongNameWidget}
        return Form


class EditPeriod(EditBase):
    VIEW_NAME = 'period'
    MODEL_CLASS = Period

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Subject.where_is_admin_or_superadmin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False,
                                          help_text=admins_help_text)
            class Meta:
                model = Period
                fields = ['parentnode', 'short_name', 'long_name', 'start_time', 'end_time', 'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                    'long_name': DevilryLongNameWidget
                    }
        return Form
