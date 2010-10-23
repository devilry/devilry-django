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

from devilry.core.models import Assignment, AssignmentGroup, \
        Deadline, Candidate
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryMultiSelectFewCandidates
from devilry.ui.fields import MultiSelectCharField
from devilry.ui.messages import UiMessages
from devilry.addons.quickdash import defaults
from devilry.ui.filtertable import AssignmentGroupsFilterTable

from shortcuts import iter_filtertable_selected



class DeadlineFormForInline(forms.ModelForm):
    """ Deadline form used in formset. """
    deadline = forms.DateTimeField(widget=DevilryDateTimeWidget)
    text = forms.CharField(required=False,
            widget=forms.Textarea(attrs=dict(rows=5, cols=50)))
    class Meta:
        model = Deadline

class DeadlineForm(forms.ModelForm):
    """ Deadline form used for standalone. """
    class Meta:
        model = Deadline
        fields = ["deadline", "text"]
        widgets = {
                'deadline': DevilryDateTimeWidget,
                'text': forms.Textarea(attrs=dict(rows=12, cols=70))
                }


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
            fields = ['name', 'examiners', 'is_open', 'points',
                    'is_passing_grade']
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


def _groups_from_filtertable(request):
    groups = []
    for key, group_id in iter_filtertable_selected(request.POST,
            'assignmentgroup'):
        group = get_object_or_404(AssignmentGroup, id=group_id)
        groups.append((key, group))
    if len(groups) == 0:
        raise GroupCountError(request)


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
        try:
            groups = _groups_from_filtertable(request)
        except GroupCountError, e:
            return e.get_response(assignment_id)

        if 'onsite' in request.POST:
            form = ExaminerForm(request.POST)
            if form.is_valid():
                examiner_ids = MultiSelectCharField.from_string(
                        form.cleaned_data['users'])
                groupobjs = [group for key, group in groups]
                examinerobjs = [User.objects.get(id=id)
                        for id in examiner_ids]
                result = random_distribute_examiners(assignment, groupobjs,
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
def create_deadline(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    
    if request.method == 'POST':
        datetimefullformat = '%Y-%m-%d %H:%M:%S'
        groups = AssignmentGroupsFilterTable.get_selected_groups(request)
        ids = [g.id for g in groups]
        selected_deadlines = Deadline.objects.filter(
                assignment_group__in=ids)
        distinct_deadlines = selected_deadlines.values('deadline').distinct()
        deadlines = [('', _("- Create a new deadline -"))]
        for d in distinct_deadlines:
            deadline = d['deadline']
            with_same = selected_deadlines.filter(deadline=deadline).count()
            if with_same == len(groups):
                deadlines.append((
                        deadline.strftime(datetimefullformat),
                        deadline.strftime(defaults.DATETIME_FORMAT)))
        has_shared_deadlines = len(deadlines) > 1

            
        class DeadlineSelectForm(forms.Form):
            deadline_to_copy = forms.ChoiceField(choices=deadlines,
                    required=False,
                    label = _("Deadline"))

        if 'onsite' in request.POST:
            deadline = Deadline(assignment_group=groups[0][1])
            deadlineform = DeadlineForm(request.POST, instance=deadline)
            selectform = DeadlineSelectForm(request.POST)
            if selectform.is_valid() and deadlineform.is_valid():
                deadline = deadlineform.cleaned_data['deadline']
                text = deadlineform.cleaned_data['text']
                deadline_to_copy = request.POST.get('deadline_to_copy', '')
                if deadline_to_copy:
                    deadline_to_copy = datetime.strptime(deadline_to_copy,
                            datetimefullformat)
                    for d in selected_deadlines.filter(deadline=deadline_to_copy):
                        d.delete()
                for key, group in groups:
                    group.deadlines.create(deadline=deadline, text=text)
                messages = UiMessages()
                messages.add_success(_('Deadlines created successfully.'))
                messages.save(request)
                return HttpResponseRedirect(reverse(
                    'devilry-admin-edit_assignment',
                    args=[assignment_id]))
        else:
            deadlineform = DeadlineForm()
            selectform = DeadlineSelectForm()
        return render_to_response('devilry/admin/create_deadline.django.html', {
                'assignment': assignment,
                'deadlineform': deadlineform,
                'selectform': selectform,
                'has_shared_deadlines': has_shared_deadlines,
                'groups': groups,
                'checkbox_name': AssignmentGroupsFilterTable.get_checkbox_name()
                }, context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest()


@login_required
def clear_deadlines(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    
    if request.method == 'POST':
        try:
            groups = _groups_from_filtertable(request)
        except GroupCountError, e:
            return e.get_response(assignment_id)
        ids = [g.id for key, g in groups]
        selected_deadlines = Deadline.objects.filter(
                assignment_group__in=ids)
        for d in selected_deadlines:
            d.delete()
        messages = UiMessages()
        messages.add_success(
                _('Deadlines successfully cleared from: %(groups)s.' %
                {'groups': ', '.join([str(g) for k, g in groups])}))
        messages.save(request)
        return HttpResponseRedirect(reverse(
            'devilry-admin-edit_assignment',
            args=[assignment_id]))
    else:
        return HttpResponseBadRequest()
