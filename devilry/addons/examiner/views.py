from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django import forms

from devilry.core.utils.GroupNodes import group_assignments
from devilry.core.models import Delivery, AssignmentGroup, Assignment, Deadline
from devilry.core import gradeplugin
from devilry.ui.widgets import DevilryDateTimeWidget
from devilry.ui.messages import UiMessages
from devilry.ui.filtertable import Columns, Col
from devilry.addons.admin.assignmentgroup_filtertable import (
        AssignmentGroupsFilterTableBase, AssignmentGroupsAction,
        FilterStatus, FilterIsPassingGrade, FilterNumberOfCandidates,
        FilterAfterDeadline)
from devilry.core.utils.delivery_collection import create_zip_from_assignmentgroups
from devilry.core.utils.assignmentgroup import GroupDeliveriesByDeadline


class DeadlineForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=DevilryDateTimeWidget,
            help_text=_('The exact date and time of the deadline.'))
    text = forms.CharField(required=False,
           widget=forms.Textarea(attrs=dict(rows=10,
               cols=70)),
           help_text=_('A optional text about the deadline. You could use '\
               'this to tell the student something extra about the ' \
               'deadline. (Example: "this is your last chance").'))
    
    class Meta:
        model = Deadline
        fields = ['deadline', 'text']

    def clean(self):
        return self.cleaned_data



class AssignmentGroupsExaminerFilterTable(AssignmentGroupsFilterTableBase):
    id = 'assignmentgroups-examiner-filtertable'
    has_related_actions = False
    has_selection_actions = True
    default_order_by = 'status'

    selectionactions = [
        AssignmentGroupsAction(_("Download deliveries"),
                               'devilry-examiner-download_file_collection'),
    ]
    

    def __init__(self, request, assignment, assignmentgroups):
        self.assignmentgroups = assignmentgroups
        super(AssignmentGroupsExaminerFilterTable, self).__init__(request,
                assignment)

    def get_filters(self):
        filters = [
            FilterStatus(),
            FilterIsPassingGrade(),
            FilterAfterDeadline(),
        ]
        numcan = FilterNumberOfCandidates(self.assignment)
        if not (numcan.maximum == 1 and numcan.minimum == 1):
            filters.append(numcan)
        return filters

    def get_columns(self):
        return Columns(
            Col('id', "Id", optional=True),
            Col('candidates', "Candidates"),
            Col('examiners', "Examiners", optional=True),
            Col('name', "Name", can_order=True, optional=True,
                active_default=True),
            Col('deadlines', "Deadlines", optional=True),
            Col('active_deadline', "Active deadline", optional=True),
            Col('latest_delivery', "Latest delivery", optional=True,
                can_order=True),
            Col('deliveries_count', "Deliveries", optional=True,
                can_order=True),
            Col('scaled_points', "Points", optional=True, can_order=True),
            Col('grade', "Grade", optional=True),
            Col('status', "Status", can_order=True, optional=True,
                active_default=True))

    def create_row(self, group, active_optional_cols):
        row = super(AssignmentGroupsExaminerFilterTable, self).create_row(
                group, active_optional_cols)
        row.add_action(_("show"), 
                       reverse('devilry-examiner-show_assignmentgroup-as-examiner',
                            args=[str(group.id)]))
        #if group.deliveries_count > 0:
            #pk = str(group.get_latest_delivery().id)
            #row.add_action(_("latest delivery"), 
                           #reverse('devilry-examiner-edit-feedback-as-examiner',
                                #args=[pk]))
        return row

    def get_assignmentgroups(self):
        return self.assignmentgroups.all()


@login_required
def list_assignments(request):
    assignments = Assignment.active_where_is_examiner(request.user)
    if assignments.count() == 0:
        return HttpResponseForbidden("Forbidden")
    subjects = group_assignments(assignments)
    is_admin = Assignment.where_is_admin_or_superadmin(request.user).count() > 0
    return render_to_response(
            'devilry/examiner/list_assignments.django.html', {
            'page_heading': _("Assignments"),
            'is_admin': is_admin,
            'subjects': subjects,
            }, context_instance=RequestContext(request))


@login_required
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    if assignment_groups.count() == 0:
        return HttpResponseForbidden("Forbidden")
    tbl = AssignmentGroupsExaminerFilterTable.initial_html(request,
            reverse('devilry-examiner-list_assignmentgroups_json',
                args=[str(assignment_id)]))
    return render_to_response(
            'devilry/examiner/list_assignmentgroups.django.html', {
                'filtertbl': tbl,
                'assignment': assignment,
                'is_admin': assignment.can_save(request.user)
            }, context_instance=RequestContext(request))


@login_required
def list_assignmentgroups_json(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    if assignment_groups.count() == 0:
        return HttpResponseForbidden("Forbidden")
    a = AssignmentGroupsExaminerFilterTable(request, assignment,
            assignment_groups)
    return a.json_response()



@login_required
def delete_deadline(request, assignmentgroup_id, deadline_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.can_examine(request.user):
        return HttpResponseForbidden("Forbidden")
    deadline = get_object_or_404(Deadline, pk=deadline_id)
    deadline.delete()
    messages = UiMessages()
    messages.add_success(_('Deadline "%(deadline)s" successfully deleted.' %
        dict(deadline=deadline)))
    messages.save(request)
    return HttpResponseRedirect(reverse(
            'devilry-examiner-show_assignmentgroup',
            args=[assignmentgroup_id]))



def _close_open_assignmentgroup(request, assignmentgroup_id, is_open, msg):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.can_examine(request.user):
        return HttpResponseForbidden("Forbidden")
    assignment_group.is_open = is_open;
    assignment_group.save()
    messages = UiMessages()
    messages.add_success(msg)
    messages.save(request)
    return HttpResponseRedirect(reverse(
            'devilry-examiner-show_assignmentgroup',
            args=[assignmentgroup_id]))

@login_required
def close_assignmentgroup(request, assignmentgroup_id):
    return _close_open_assignmentgroup(request, assignmentgroup_id, False,
        _('Assignment group successfully closed.'))

@login_required
def open_assignmentgroup(request, assignmentgroup_id):
    return _close_open_assignmentgroup(request, assignmentgroup_id, True,
        _('Assignment group successfully opened.'))


def _handle_is_admin(request, is_admin):
    sessionkey = "is_admin"
    if is_admin == False:
        if request.session.get("is_admin"):
            del request.session['is_admin']
    if is_admin == True:
        request.session['is_admin'] = True
        request.session.save()


@login_required
def show_assignmentgroup(request, assignmentgroup_id, is_admin=None):
    _handle_is_admin(request, is_admin)
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.can_examine(request.user):
        return HttpResponseForbidden("Forbidden")

    valid_deadlineform = True
    if 'create-deadline' in request.POST:
        deadline = Deadline()
        deadline.assignment_group = assignment_group
        deadline_form = DeadlineForm(request.POST, instance=deadline)

        if deadline_form.is_valid():
            deadline.save()
            return HttpResponseRedirect(reverse(
                    'devilry-examiner-show_assignmentgroup',
                    args=[assignmentgroup_id]))
        else:
            valid_deadlineform = False
    else:
        deadline_form = DeadlineForm()
        

    show_deadline_hint = assignment_group.is_open and \
        assignment_group.status == AssignmentGroup.CORRECTED_AND_PUBLISHED

    messages = UiMessages()
    messages.load(request)
    
    dg = GroupDeliveriesByDeadline(assignment_group)
    return render_to_response(
            'devilry/examiner/show_assignmentgroup.django.html', {
                'assignment_group': assignment_group,
                'after_deadline': dg.after_last_deadline,
                'within_a_deadline': dg.within_a_deadline,
                'ungrouped_deliveries': dg.ungrouped_deliveries,
                'deadline_form': deadline_form,
                'show_deadline_hint': show_deadline_hint,
                'messages': messages,
                'valid_deadlineform': valid_deadlineform
            }, context_instance=RequestContext(request))


@login_required
def edit_feedback(request, delivery_id, is_admin=None):
    _handle_is_admin(request, is_admin)
    delivery_obj = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery_obj.assignment_group.can_examine(request.user):
        return HttpResponseForbidden("Forbidden")
    key = delivery_obj.assignment_group.parentnode.grade_plugin
    return gradeplugin.registry.getitem(key).view(request, delivery_obj)


@login_required
def download_file_collection(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    groups = AssignmentGroupsExaminerFilterTable.get_selected_groups(request)        
    #Check permission fro examiner
    for g in groups:
        if not g.can_examine(request.user):
            return HttpResponseForbidden("Forbidden: You tried to download"\
                                         "deliveries from an assignment you"\
                                         "do not have access to.")
    return create_zip_from_assignmentgroups(request, assignment, groups)
