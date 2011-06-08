from random import randint
import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
        HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory, formset_factory
from django.contrib.auth.models import User

from ...core.models import Assignment, AssignmentGroup, \
        Deadline, Candidate
from ...ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryMultiSelectFewCandidates
from ...ui.fields import MultiSelectCharField
from ...ui.messages import UiMessages
from ..assignmentgroup_filtertable import (
    AssignmentGroupsFilterTableBase, AssignmentGroupsAction, FilterStatus,
    FilterIsPassingGrade, FilterExaminer, FilterNumberOfCandidates,
    FilterMissingCandidateId, FilterAfterDeadline,
    create_deadlines_base, clear_deadlines_base,
    FilterIsOpen, open_close_many_groups_base,
    publish_many_groups_base)
from ...ui.filtertable import Columns, Col

from shortcuts import deletemany_generic

from ....utils.delivery_collection import (
        create_archive_from_assignmentgroups,
        verify_groups_not_exceeding_max_file_size)

class AssignmentGroupsFilterTable(AssignmentGroupsFilterTableBase):
    id = 'assignmentgroups-admin-filtertable'
    selectionactions = [
            AssignmentGroupsAction(_("Delete"),
                'devilry-admin-delete_manyassignmentgroups',
                confirm_title=_("Confirm delete"),
                confirm_message=_("Are you sure you want to delete "\
                    "the selected groups including their deliveries "\
                    "and feedback?")),
            AssignmentGroupsAction(_("Create/replace deadline"),
                'devilry-admin-create_deadline'),
            AssignmentGroupsAction(_("Clear deadlines"),
                'devilry-admin-clear_deadlines',
                confirm_title=_("Confirm clear deadlines"),
                confirm_message=_("Are you sure you want to clear "\
                    "deadlines on the following groups?")),
            AssignmentGroupsAction(_("Set examiners"),
                'devilry-admin-set_examiners'),
            AssignmentGroupsAction(_("Random distribute examiners"),
                                   'devilry-admin-random_dist_examiners'),

            AssignmentGroupsAction(_("Close groups"),
                'devilry-admin-close_many_groups',
                confirm_title=_("Confirm close groups"),
                confirm_message=_("Are you sure you want to close "\
                    "the selected groups?")),
            AssignmentGroupsAction(_("Open groups"),
                'devilry-admin-open_many_groups',
                confirm_title=_("Confirm open groups"),
                confirm_message=_("Are you sure you want to open "\
                    "the selected groups?")),

            AssignmentGroupsAction(_("Publish latest feedback"),
                'devilry-admin-publish_many_groups',
                confirm_title=_("Confirm publish groups"),
                confirm_message=_("Are you sure you want to publish "\
                    "the selected groups? This will send an email to each "
                    "member of every selected group.")),

            AssignmentGroupsAction(_("Download deliveries as ZIP"),
                               'devilry-admin-download_assignment_collection_as_zip'),
            AssignmentGroupsAction(_("Download deliveries as TAR"),
                               'devilry-admin-download_assignment_collection_as_tar'),
        ]
    relatedactions = [
            AssignmentGroupsAction(_("Create new group"),
                "devilry-admin-create_assignmentgroup"),
            AssignmentGroupsAction(_("Create many groups (advanced)"),
                "devilry-admin-create_assignmentgroups"),
            AssignmentGroupsAction(_("Create groups by copy"),
                "devilry-admin-copy_groups"),
            AssignmentGroupsAction(_("Examiner mode"),
                "devilry-examiner-list_assignmentgroups")
            ]

    def get_filters(self):
        filters = [
            FilterStatus(),
            FilterIsOpen(),
            FilterIsPassingGrade(),
            FilterExaminer(),
            FilterAfterDeadline(),
        ]
        numcan = FilterNumberOfCandidates(self.assignment)
        if not (numcan.maximum == 1 and numcan.minimum == 1):
            filters.append(numcan)
        if self.assignment.anonymous:
            filters.append(FilterMissingCandidateId())
        return filters

    def get_columns(self):
        return Columns(
            Col('id', "Id", optional=True),
            Col('candidates', "Candidates"),
            Col('examiners', "Examiners", optional=True, active_default=True),
            Col('name', "Name", can_order=True, optional=True,
                active_default=True),
            Col('deadlines', "Deadlines", optional=True),
            Col('active_deadline', "Active deadline", optional=True),
            Col('latest_delivery', "Latest delivery", optional=True,
                can_order=True),
            Col('deliveries_count', "Deliveries", optional=True,
                can_order=True),
            Col('scaled_points', "Points", optional=True, can_order=True),
            Col('isopen', "Open?", optional=True),
            Col('grade', "Grade", optional=True),
            Col('status', "Status", can_order=True, optional=True,
                active_default=True))

    def create_row(self, group, active_optional_cols):
        row = super(AssignmentGroupsFilterTable, self).create_row(group,
                active_optional_cols)
        row.add_action(_("edit"), 
                reverse('devilry-admin-edit_assignmentgroup',
                        args=[self.assignment.id, str(group.id)]))
        row.add_action(_("examine"), 
                       reverse('devilry-examiner-show_assignmentgroup-as-admin',
                            args=[str(group.id)]))
        #if group.deliveries_count > 0:
            #pk = str(group.get_latest_delivery().id)
            #row.add_action(_("examine"), 
                           #reverse('devilry-examiner-edit-feedback-as-admin',
                                #args=[pk]))
        return row

    def get_assignmentgroups(self):
        return self.assignment.assignmentgroups.all()



class DeadlineFormForInline(forms.ModelForm):
    """ Deadline form used in formset. """
    deadline = forms.DateTimeField(widget=DevilryDateTimeWidget)
    text = forms.CharField(required=False,
            widget=forms.Textarea(attrs=dict(rows=5, cols=50)))
    class Meta:
        model = Deadline


@login_required
def edit_assignmentgroup(request, assignment_id, assignmentgroup_id=None,
        successful_save=False):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    isnew = assignmentgroup_id == None
    if isnew:
        assignmentgroup = AssignmentGroup(parentnode=assignment)
    else:
        assignmentgroup = get_object_or_404(AssignmentGroup,
                id=assignmentgroup_id, parentnode=assignment)
    messages = UiMessages()

    if successful_save:
        messages.add_success(_("Assignment group successfully saved."))
    
    class AssignmentGroupForm(forms.ModelForm):
        #parentnode = forms.ModelChoiceField(required=True,
                #queryset = Assignment.where_is_admin(request.user))
        examiners = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb,
                                         required=False)
                    
        class Meta:
            model = AssignmentGroup
            fields = ['name', 'examiners', 'is_open']
            widgets = {
                'examiners': DevilryMultiSelectFewUsersDb,
                }

    DeadlineFormSet = inlineformset_factory(AssignmentGroup, Deadline,
            extra=1, form=DeadlineFormForInline)
    CandidatesFormSet = inlineformset_factory(AssignmentGroup,
            Candidate, extra=1)

    model_name = AssignmentGroup._meta.verbose_name
    model_name_dict = {'model_name': model_name}

    if request.method == 'POST':
        assignmentgroupform = AssignmentGroupForm(request.POST,
                instance=assignmentgroup)
        deadline_formset = DeadlineFormSet(request.POST,
                instance=assignmentgroup)
        candidates_formset = CandidatesFormSet(request.POST,
                instance=assignmentgroup)
        if assignmentgroupform.is_valid() \
                and deadline_formset.is_valid() \
                and candidates_formset.is_valid():
            if not assignmentgroup.can_save(request.user):
                return HttpResponseForbidden("Forbidden")
            assignmentgroupform.save()
            deadline_formset.save()
            candidates_formset.save()
            success_url = reverse('devilry-admin-edit_assignmentgroup-success',
                    args=[str(assignment.id), str(assignmentgroup.id)])
            return HttpResponseRedirect(success_url)
    else:
        assignmentgroupform = AssignmentGroupForm(instance=assignmentgroup)
        deadline_formset = DeadlineFormSet(instance=assignmentgroup)
        candidates_formset = CandidatesFormSet(instance=assignmentgroup)

    return render_to_response('devilry/admin/edit_assignmentgroup.django.html', {
        'assignment': assignment,
        'assignmentgroup': assignmentgroup,
        'assignmentgroupform': assignmentgroupform,
        'deadline_form': deadline_formset,
        'candidates_form': candidates_formset,
        'messages': messages,
        'isnew': isnew,
        }, context_instance=RequestContext(request))

@login_required
def save_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    return CreateAssignmentgroups().save_assignmentgroups(request, assignment)



class AssignmentgroupForm(forms.Form):
    name = forms.CharField(required=False)
    candidates = forms.CharField(widget=DevilryMultiSelectFewCandidates, required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get("name")
        candidates = cleaned_data.get("candidates").strip()

        # Verify that the usernames are valid
        if candidates != '':
            sep = re.compile(r'\s*,\s*')
            cands = sep.split(candidates)
            for cand in cands:
                if cand == '':
                    continue
                cand = cand.split(":")[0].strip()
                if User.objects.filter(username=cand).count() == 0:
                    raise forms.ValidationError("User %s could not be found." % (cand))
        
        # Always return the full collection of cleaned data.
        return cleaned_data


class CreateAssignmentgroups(object):
    def save_assignmentgroups(self, request, assignment, initial_data=None):
        """
        If ``initial_data`` is set, saving is skipped. 
        """
        if request.POST:
            AssignmentGroupsFormSet = formset_factory(AssignmentgroupForm,
                    extra=0)
            if initial_data:
                formset = AssignmentGroupsFormSet(initial=initial_data)
            else:
                formset = AssignmentGroupsFormSet(request.POST)

            messages = UiMessages()

            if not initial_data:
                if not formset.is_valid():
                    messages.add_error(_("There is an error in the input data."))
                else:                
                    success = True

                    for i in range(0, formset.total_form_count()):
                        form = formset.forms[i]
                        name = ''
                        candidates = ''
                        
                        if 'name' in form.cleaned_data:
                            name = form.cleaned_data['name']
                        
                        if 'candidates' in form.cleaned_data:
                            candidates = form.cleaned_data['candidates']
                            
                        if name != '' or candidates != '':
                            if not self.save_group(assignment, name, candidates):
                                messages.add_error(_("Failed to save group") + name + ":" + candidates)
                                success = False
                                break
                    if success:                        
                        return HttpResponseRedirect(reverse(
                                'devilry-admin-edit_assignment', args=[assignment.id]))
            return render_to_response(
                'devilry/admin/verify_assignmentgroups.django.html', {
                    'formset': formset,
                    'assignment': assignment,
                    'messages': messages,
                    }, context_instance=RequestContext(request))
        else:
            return HttpResponseForbidden('Forbidden')

    def save_group(self, assignment, name, candidates):
        ag = AssignmentGroup()
        ag.parentnode = assignment
        if name:
            ag.name = name
        ag.save()
        if candidates:
            candidates = candidates.strip()
            sep = re.compile(r'\s*,\s*')
            candsplit = sep.split(candidates)
            for user in candsplit:
                if user == '':
                    continue
                user_cand = user.split(':')
                try:
                    userobj = User.objects.get(username=user_cand[0])
                    cand = Candidate()
                    cand.student = userobj
                    cand.assignment_group = ag
                    
                    if len(user_cand) == 2 and user_cand[1].isdigit():
                        cand.candidate_id = user_cand[1]
                    cand.save()
                    ag.candidates.add(cand)
                    ag.save()
                except Exception, e:
                    #print "user %s doesnt exist" % (user_cand)
                    return False

        return True
       

@login_required
def create_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    class Form(forms.Form):
        assignment_groups = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':30, 'cols':70}))

    if request.POST:
        form = Form(request.POST) 
        if form.is_valid():
            groups = form.cleaned_data['assignment_groups']
            lines = groups.splitlines()
            initial_data = []
            
            for l in lines:
                if l.strip() == "":
                    continue
                m = re.match("(?:(?P<name>.+?)::)?\s*(?P<users>.+)?", l)
                if not m:
                    continue
                
                group_data = {}
                name = m.group('name')
                users = m.group('users')
                if name:
                    group_data['name'] = name
                if users:
                    group_data['candidates'] = users
                initial_data.append(group_data)
            return CreateAssignmentgroups().save_assignmentgroups(request,
                    assignment, initial_data)
    else:
        form = Form()

    return render_to_response('devilry/admin/create_assignmentgroups.django.html', {
            'form': form,
            'assignment': assignment,
            }, context_instance=RequestContext(request))



class GroupCountError(Exception):
    def __init__(self, request):
        self.request = request

    def get_response(self, assignment_id):
        messages = UiMessages()
        messages.add_error(_('Select at least one assignment group.'))
        messages.save(self.request)
        return HttpResponseRedirect(reverse(
            'devilry-admin-edit_assignment',
            args=[assignment_id]))



@login_required
def set_examiners(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    class ExaminerForm(forms.Form):
         examiners = forms.CharField(widget=DevilryMultiSelectFewCandidates,
                required=False,
                help_text=_('Usernames separated by ",". Leave empty to '\
                    'clear examiners'))
    if request.method == 'POST':
        groups = AssignmentGroupsFilterTable.get_selected_groups(request)

        if 'onsite' in request.POST:
            form = ExaminerForm(request.POST)
            if form.is_valid():
                examiners = form.cleaned_data['examiners']
                user_ids = MultiSelectCharField.from_string(examiners)
                for group in groups:
                    group.examiners.clear()
                    for id in user_ids:
                        group.examiners.add(User.objects.get(id=id))
                messages = UiMessages()
                if user_ids:
                    messages.add_success(_('Examiners successfully changed'))
                else:
                    messages.add_success(_('Examiners successfully cleared'))
                messages.save(request)
                return HttpResponseRedirect(reverse(
                    'devilry-admin-edit_assignment',
                    args=[assignment_id]))
        else:
            form = ExaminerForm()

        return render_to_response('devilry/admin/set-examiners.django.html', {
                'form': form,
                'assignment': assignment,
                'groups': groups,
                'checkbox_name': AssignmentGroupsFilterTable.get_checkbox_name()
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest()



def random_distribute_examiners(assignment, assignmentgroups, examiners):
    assignments_per_examiner = len(assignmentgroups) / len(examiners)
    result = {}
    for examiner in examiners:
        groups = []
        for x in xrange(assignments_per_examiner):
            r = randint(0, len(assignmentgroups)-1)
            group = assignmentgroups[r]
            del assignmentgroups[r]
            groups.append(group)
            group.examiners.clear()
            group.examiners.add(examiner)
        result[examiner.username] = groups
    if len(assignmentgroups) > 0:
        # Distribute the rest, if assignmentgroups is not dividable on
        # examiners
        for group in assignmentgroups:
            r = randint(0, len(examiners)-1)
            examiner = examiners[r]
            del examiners[r]
            result[examiner.username].append(group)
            group.examiners.add(examiner)
    return result

@login_required
def random_dist_examiners(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    class ExaminerForm(forms.Form):
        users = forms.CharField(widget=DevilryMultiSelectFewCandidates,
                required=True)
    if request.method == 'POST':
        groups = AssignmentGroupsFilterTable.get_selected_groups(request)

        if 'onsite' in request.POST:
            form = ExaminerForm(request.POST)
            if form.is_valid():
                examiner_ids = MultiSelectCharField.from_string(
                        form.cleaned_data['users'])
                examinerobjs = [User.objects.get(id=id)
                        for id in examiner_ids]
                result = random_distribute_examiners(assignment,
                        [g for g in groups],
                        examinerobjs)
                m = ['<p>', _('Examiners successfully random distributed.'), '</p>']
                for examiner, assignmentgroups in result.iteritems():
                    m.append('%s:<ul>%s</ul>' % (
                            examiner,
                            '\n'.join(['<li>%s</li>' % g.get_candidates()
                                for g in assignmentgroups])))
                messages = UiMessages()
                messages.add_success('\n'.join(m), raw_html=True)
                messages.save(request)
                return HttpResponseRedirect(reverse(
                    'devilry-admin-edit_assignment',
                    args=[assignment_id]))
        else:
            form = ExaminerForm()

        return render_to_response('devilry/admin/random-dist-examiners.django.html', {
                'form': form,
                'assignment': assignment,
                'checkbox_name': AssignmentGroupsFilterTable.get_checkbox_name(),
                'groups': groups
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest()



@login_required
def copy_groups(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    
    assignments_in_period = Assignment.where_is_admin_or_superadmin(
            request.user).filter(parentnode=assignment.parentnode).exclude(
                    id=assignment.id)
    class AssignmentSelectForm(forms.Form):
        assignment = forms.ModelChoiceField(queryset=assignments_in_period,
                empty_label=None,
                label = _("Assignments"))

    if request.method == 'POST':
        form = AssignmentSelectForm(request.POST)
        if form.is_valid():
            copy_assignment = form.cleaned_data['assignment']
            for copy_group in copy_assignment.assignmentgroups.all():
                group = AssignmentGroup(parentnode=assignment)
                group.name = copy_group.name
                group.save()
                for examiner in copy_group.examiners.all():
                    group.examiners.add(examiner)
                for copy_candidate in copy_group.candidates.all():
                    candidate = Candidate()
                    candidate.student = copy_candidate.student
                    candidate.candidate_id = copy_candidate.candidate_id
                    group.candidates.add(candidate)
                assignment.assignmentgroups.add(group)
            assignment.save()
            messages = UiMessages()
            messages.add_success(_('Assignment groups successfully copied.'))
            messages.save(request)
            return HttpResponseRedirect(reverse(
                'devilry-admin-edit_assignment',
                args=[assignment_id]))
    else:
        form = AssignmentSelectForm()
    return render_to_response('devilry/admin/copy-groups.django.html', {
            'assignment': assignment,
            'form': form,
            'assignments_in_period': assignments_in_period,
            }, context_instance=RequestContext(request))



@login_required
def delete_manyassignmentgroups(request, assignment_id):
    return deletemany_generic(request, AssignmentGroup,
            AssignmentGroupsFilterTable,
            successurl=reverse('devilry-admin-edit_assignment',
                args=[assignment_id]))

@login_required
def download_assignment_collection(request, assignment_id, archive_type=None):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    #Check admin rights
    if assignment.can_save(request.user):
        groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    else:
        return HttpResponseForbidden("Forbidden: You tried to download deliveries "\
                                     "from an assignment you do not have access to.")
    if archive_type == "zip":
        try:
            verify_groups_not_exceeding_max_file_size(groups)
        except Exception, e:
            return HttpResponseForbidden(_("One or more files exeeds the maximum file size for ZIP files."))
    return create_archive_from_assignmentgroups(request, groups, assignment.get_path(), archive_type)



@login_required
def create_deadline(request, assignment_id):
    groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    return create_deadlines_base(request, assignment_id, groups,
            AssignmentGroupsFilterTable.get_checkbox_name(),
            'devilry-admin-edit_assignment',
            'devilry-admin-create_deadline',
            'devilry/admin/create_deadline.django.html')

@login_required
def clear_deadlines(request, assignment_id):
    groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    return clear_deadlines_base(request, assignment_id, groups,
            'devilry-admin-edit_assignment')


@login_required
def close_many_groups(request, assignment_id):
    groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    redirect_to = reverse('devilry-admin-edit_assignment',
                args=[str(assignment_id)])
    return open_close_many_groups_base(request, assignment_id, groups,
            redirect_to, is_open=False)

@login_required
def open_many_groups(request, assignment_id):
    groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    redirect_to = reverse('devilry-admin-edit_assignment',
                args=[str(assignment_id)])
    return open_close_many_groups_base(request, assignment_id, groups,
            redirect_to, is_open=True)




@login_required
def publish_many_groups(request, assignment_id):
    groups = AssignmentGroupsFilterTable.get_selected_groups(request)
    redirect_to = reverse('devilry-admin-edit_assignment',
                args=[str(assignment_id)])
    return publish_many_groups_base(request, assignment_id, groups, redirect_to)
