from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden

from devilry.ui.filtertable import Columns, Col, Row
from devilry.core.models import Node, Subject
from devilry.ui.widgets import (DevilryMultiSelectFewUsersDb,
        DevilryLongNameWidget)
from devilry.ui.fields import MultiSelectCharField

from shortcuts import (BaseNodeFilterTable, NodeAction, EditBase,
        deletemany_generic, admins_help_text, FilterHasAdmins)


class SubjectFilterTable(BaseNodeFilterTable):
    id = 'subject-admin-filtertable'
    nodecls = Subject

    selectionactions = [
        NodeAction(_("Delete"),
            'devilry-admin-delete_manysubjects',
            confirm_title = _("Confirm delete"),
            confirm_message = \
                _('This will delete all selected subjects and all periods, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            )]
    relatedactions = [
        NodeAction(_("Create new"), 'devilry-admin-create_subject')]

    def get_columns(self):
        return Columns(
            Col('short_name', "Short name", can_order=True),
            Col('long_name', "Long name", can_order=True, optional=True),
            Col('parent', "Parent"),
            Col('admins', "Administrators", optional=True))

    def create_row(self, subject, active_optional_cols):
        row = Row(subject.id, title=unicode(subject))
        row.add_cell(subject.short_name)
        if "long_name" in active_optional_cols:
            row.add_cell(subject.long_name)
        row.add_cell(subject.parentnode or "")
        if "admins" in active_optional_cols:
            row.add_cell(subject.get_admins())
        row.add_action(_("edit"), 
                reverse('devilry-admin-edit_subject', args=[str(subject.id)]))
        return row


class EditSubject(EditBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

    def get_parent_url(self):
        return reverse('devilry-admin-list_subjects')

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



@login_required
def list_subjects_json(request):
    tbl = SubjectFilterTable(request)
    return tbl.json_response()

@login_required
def list_subjects(request, *args, **kwargs):
    if not request.user.is_superuser \
            and Subject.where_is_admin_or_superadmin(request.user).count() == 0:
        return HttpResponseForbidden("Forbidden")
    tbl = SubjectFilterTable.initial_html(request,
            reverse('devilry-admin-list_subjects_json'))
    return render_to_response('devilry/admin/list-nodes-generic.django.html', {
        'title': _("Subjects"),
        'filtertbl': tbl
        }, context_instance=RequestContext(request))


@login_required
def edit_subject(request, subject_id=None):
    return EditSubject(request, subject_id).create_view()

@login_required
def delete_manysubjects(request):
    return deletemany_generic(request, Subject, SubjectFilterTable,
            reverse('devilry-admin-list_subjects'))
