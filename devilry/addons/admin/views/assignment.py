from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _

from devilry.core.models import Period, Assignment
from devilry.ui.messages import UiMessages
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryLongNameWidget
from devilry.ui.fields import MultiSelectCharField
from devilry.core import gradeplugin
from devilry.ui.filtertable import Columns, Col, Row

from assignmentgroup import AssignmentGroupsFilterTable
from shortcuts import (BaseNodeFilterTable, NodeAction,
        deletemany_generic)


class AssignmentFilterTable(BaseNodeFilterTable):
    id = 'assignment-admin-filtertable'
    nodecls = Assignment
    default_order_by = "publishing_time"
    default_order_asc = False

    selectionactions = [
        NodeAction(_("Delete"),
            'devilry-admin-delete_manyassignments',
            confirm_title = _("Confirm delete"),
            confirm_message = \
                _('This will delete all selected assignments and all assignments, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            )]
    relatedactions = [
        NodeAction(_("Create new"), 'devilry-admin-create_assignment')]

    def get_columns(self):
        return Columns(
            Col('short_name', "Short name", can_order=True),
            Col('long_name', "Long name", optional=True, can_order=True),
            Col('parentnode', "Parent", can_order=True,
                optional=True, active_default=True),
            Col('publishing_time', "Publishing time", can_order=True,
                optional=True, active_default=True),
            Col('admins', "Administrators", optional=True))

    def create_row(self, assignment, active_optional_cols):
        row = Row(assignment.id, title=unicode(assignment))
        row.add_cell(assignment.short_name)
        if "long_name" in active_optional_cols:
            row.add_cell(assignment.long_name)
        if "parentnode" in active_optional_cols:
            row.add_cell(assignment.parentnode or "")
        if "publishing_time" in active_optional_cols:
            row.add_cell(assignment.publishing_time)
        if "admins" in active_optional_cols:
            row.add_cell(assignment.get_admins())
        row.add_action(_("edit"), 
                reverse('devilry-admin-edit_assignment', args=[str(assignment.id)]))
        return row

    
    def search(self, dataset, qry):
        return dataset.filter(
                Q(parentnode__parentnode__short_name__contains=qry) |
                Q(parentnode__short_name__contains=qry) |
                Q(short_name__contains=qry) |
                Q(long_name__contains=qry) |
                Q(admins__username__contains=qry))



@login_required
def edit_assignment(request, assignment_id=None):
    isnew = assignment_id == None
    if isnew:
        assignment = Assignment()
    else:
        assignment = get_object_or_404(Assignment, id=assignment_id)
        if not assignment.can_save(request.user):
            return HttpResponseForbidden("Forbidden")
    messages = UiMessages()
    messages.load(request)

    class Form(forms.ModelForm):
        parentnode = forms.ModelChoiceField(required=True,
                queryset = Period.not_ended_where_is_admin_or_superadmin(request.user))
        admins = MultiSelectCharField(required=False,
                widget=DevilryMultiSelectFewUsersDb)
        class Meta:
            model = Assignment
            fields = ['parentnode', 'short_name', 'long_name', 
                    'publishing_time', 'filenames', 'admins', 'anonymous',
                    'must_pass', 'pointscale', 'autoscale']
            if isnew:
                fields.append('grade_plugin')
            widgets = {
                'publishing_time': DevilryDateTimeWidget,
                'long_name': DevilryLongNameWidget
                }

    if not isnew:
        gp = gradeplugin.registry.getitem(assignment.grade_plugin)
        msg = _('This assignment uses the <em>%(gradeplugin_label)s</em> ' \
                'grade-plugin. You cannot change grade-plugin on an ' \
                'existing assignment.' % {'gradeplugin_label': gp.label})
        if gp.admin_url_callback:
            url = gp.admin_url_callback(assignment.id)
            msg2 = _('<a href="%(gradeplugin_admin_url)s">Click here</a> '\
                    'to administer the plugin.' % {'gradeplugin_admin_url': url})
            messages.add_info('%s %s' % (msg, msg2), raw_html=True)
        else:
            messages.add_info(msg, raw_html=True)
    
    if request.method == 'POST':
        form = Form(request.POST, instance=assignment)
        if form.is_valid():
            if not assignment.can_save(request.user):
                return HttpResponseForbidden("Forbidden")
            form.save()
            messages = UiMessages()
            messages.add_success(_('Assignment successfully saved.'))
            messages.save(request)
            success_url = reverse('devilry-admin-edit_assignment',
                    args=[str(assignment.pk)])
            return HttpResponseRedirect(success_url)
    else:
        form = Form(instance=assignment)

    if not isnew:
        examiners = User.objects.filter(examiners__parentnode=assignment).distinct()
    else:
        examiners = []


    if isnew:
        assignmentgroupstbl = None
    else:
        assignmentgroupstbl = AssignmentGroupsFilterTable.initial_html(request,
                reverse("devilry-admin-assignmentgroups-json",
                    args=[str(assignment.id)]))
    return render_to_response('devilry/admin/edit_assignment.django.html', {
        'form': form,
        'assignment': assignment,
        'messages': messages,
        'isnew': isnew,
        'gradeplugins': gradeplugin.registry.iteritems(),
        'examiners': examiners,
        'assignmentgroupstbl': assignmentgroupstbl
        }, context_instance=RequestContext(request))


@login_required
def list_assignments_json(request):
    tbl = AssignmentFilterTable(request)
    return tbl.json_response()

@login_required
def list_assignments(request, *args, **kwargs):
    if not request.user.is_superuser \
            and Assignment.where_is_admin_or_superadmin(request.user).count() == 0:
        return HttpResponseForbidden("Forbidden")
    tbl = AssignmentFilterTable.initial_html(request,
            reverse('devilry-admin-list_assignments_json'))
    messages = UiMessages()
    messages.load(request)
    return render_to_response('devilry/admin/list-nodes-generic.django.html', {
        'title': _("Assignments"),
        'messages': messages,
        'filtertbl': tbl
        }, context_instance=RequestContext(request))


@login_required
def delete_manyassignments(request):
    return deletemany_generic(request, Assignment, AssignmentFilterTable,
            reverse('devilry-admin-list_assignments'))


@login_required
def assignmentgroups_json(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    a = AssignmentGroupsFilterTable(request, assignment)
    return a.json_response()
