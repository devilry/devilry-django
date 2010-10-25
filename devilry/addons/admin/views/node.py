from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden

from devilry.ui.filtertable import Columns, Col, Row
from devilry.core.models import Node
from devilry.ui.widgets import (DevilryMultiSelectFewUsersDb,
        DevilryLongNameWidget)
from devilry.ui.fields import MultiSelectCharField

from shortcuts import (BaseNodeFilterTable, NodeAction, EditBase,
        deletemany_generic, admins_help_text, FilterHasAdmins)


class NodeFilterTable(BaseNodeFilterTable):
    id = 'node-admin-filtertable'
    nodecls = Node
    use_rowactions = True
    filters = [FilterHasAdmins()]

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
            Col('shortname', "Short name", can_order=True),
            Col('longname', "Long name", optional=True,
                can_order=True),
            Col('parent', "Parent"),
            Col('admins', "Administrators", optional=True),
            )

    def create_row(self, node, active_optional_cols):
        row = Row(node.id, title=unicode(node))
        row.add_cell(node.short_name)
        if "longname" in active_optional_cols:
            row.add_cell(node.long_name)
        row.add_cell(unicode(node.parentnode or ""))
        if "admins" in active_optional_cols:
            row.add_cell(node.get_admins())
        row.add_action(_("edit"), 
                reverse('devilry-admin-edit_node', args=[str(node.id)]))
        return row
    
    def order_by(self, dataset, colnum, order_asc):
        prefix = '-'
        if order_asc:
            prefix = ''
        return dataset.order_by(prefix + "short_name")


class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def get_parent_url(self):
        return reverse('devilry-admin-list_nodes')

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(
                    required=False,
                    queryset = Node.where_is_admin_or_superadmin(self.request.user))
            admins = MultiSelectCharField(
                    widget=DevilryMultiSelectFewUsersDb, 
                    required=False,
                    help_text=admins_help_text)
            class Meta:
                model = Node
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
                widgets = {'long_name': DevilryLongNameWidget}
        return NodeForm



@login_required
def list_nodes_json(request):
    tbl = NodeFilterTable(request)
    return tbl.json_response()

@login_required
def list_nodes(request, *args, **kwargs):
    if not request.user.is_superuser \
            and Node.where_is_admin_or_superadmin(request.user).count() == 0:
        return HttpResponseForbidden("Forbidden")
    tbl = NodeFilterTable.initial_html(request,
            reverse('devilry-admin-list_nodes_json'))
    return render_to_response('devilry/admin/list-nodes-generic.django.html', {
        'title': _("Nodes"),
        'filtertbl': tbl
        }, context_instance=RequestContext(request))


@login_required
def edit_node(request, node_id=None):
    return EditNode(request, node_id).create_view()


@login_required
def delete_manynodes(request):
    return deletemany_generic(request, Node, NodeFilterTable,
            reverse('devilry-admin-list_nodes'))
