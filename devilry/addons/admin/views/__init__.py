from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from devilry.core.models import Node, Subject, Period, Assignment, \
        AssignmentGroup
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryLongNameWidget
from devilry.ui.fields import MultiSelectCharField
from devilry.ui.filtertable import (Filter, Action, FilterTable, Columns,
        Col, Row)

from shortcuts import EditBase, deletemany_generic, admins_help_text
from assignment import edit_assignment



class BaseNodeFilterTable(FilterTable):
    nodecls = None
    search_help = _("Search for any part of the short name.")

    @classmethod
    def get_selected_nodes(cls, request):
        nodes = []
        for node_id in cls.get_selected_ids(request):
            node = get_object_or_404(cls.nodecls, id=node_id)
            if node.can_save(request.user):
                nodes.append(node)
        return nodes

    def __init__(self, request):
        super(BaseNodeFilterTable, self).__init__(request)
        self.set_properties(nodecls=self.nodecls)

    def create_dataset(self):
        dataset = self.nodecls.where_is_admin_or_superadmin(self.request.user)
        total = dataset.count()
        return total, dataset

    def search(self, dataset, qry):
        return dataset.filter(
                short_name__contains=qry)


class NodeAction(Action):
    def get_url(self, properties):
        return reverse(self.url)


class NodeFilterTable(BaseNodeFilterTable):
    id = 'node-admin-filtertable'
    nodecls = Node

    selectionactions = [
        NodeAction(_("Delete"),
            'devilry-admin-delete_manynodes',
            confirm_title = _("Confirm delete"),
            confirm_message = \
                _('This will delete all selected nodes and all subjects, periods, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            )]
    relatedactions = [
        NodeAction(_("Create new"), 'devilry-admin-create_node')]

    def get_columns(self):
        return Columns(
            Col('name', "Short name", can_order=True),
            Col('parent', "Parent"))

    def create_row(self, node, active_optional_cols):
        row = Row(node.id, title=unicode(node))
        row.add_cell(node.short_name)
        row.add_cell(unicode(node.parentnode or ""))
        return row
    
    def order_by(self, dataset, colnum, order_asc):
        prefix = '-'
        if order_asc:
            prefix = ''
        return dataset.order_by(prefix + "short_name")


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
    return deletemany_generic(request, Node, NodeFilterTable)

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
                fields = ['parentnode', 'short_name', 'long_name',
                        'start_time', 'end_time', 'minimum_points',
                        'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                    'long_name': DevilryLongNameWidget
                    }
        return Form
