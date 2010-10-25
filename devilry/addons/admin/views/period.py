from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden

from devilry.ui.filtertable import Columns, Col, Row
from devilry.core.models import Subject, Period
from devilry.ui.widgets import (DevilryMultiSelectFewUsersDb,
        DevilryLongNameWidget, DevilryDateTimeWidget)
from devilry.ui.fields import MultiSelectCharField

from shortcuts import (BaseNodeFilterTable, NodeAction, EditBase,
        deletemany_generic, admins_help_text)


class PeriodFilterTable(BaseNodeFilterTable):
    id = 'period-admin-filtertable'
    nodecls = Period

    selectionactions = [
        NodeAction(_("Delete"),
            'devilry-admin-delete_manyperiods',
            confirm_title = _("Confirm delete"),
            confirm_message = \
                _('This will delete all selected periods and all periods, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            )]
    relatedactions = [
        NodeAction(_("Create new"), 'devilry-admin-create_period')]

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


class EditPeriod(EditBase):
    VIEW_NAME = 'period'
    MODEL_CLASS = Period

    def get_parent_url(self):
        return reverse('devilry-admin-list_periods')

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



@login_required
def list_periods_json(request):
    tbl = PeriodFilterTable(request)
    return tbl.json_response()

@login_required
def list_periods(request, *args, **kwargs):
    if not request.user.is_superuser \
            and Period.where_is_admin_or_superadmin(request.user).count() == 0:
        return HttpResponseForbidden("Forbidden")
    tbl = PeriodFilterTable.initial_html(request,
            reverse('devilry-admin-list_periods_json'))
    return render_to_response('devilry/admin/list-nodes-generic.django.html', {
        'title': _("Periods"),
        'filtertbl': tbl
        }, context_instance=RequestContext(request))


@login_required
def edit_period(request, period_id=None):
    return EditPeriod(request, period_id).create_view()

@login_required
def delete_manyperiods(request):
    return deletemany_generic(request, Period, PeriodFilterTable,
            reverse('devilry-admin-list_periods'))
