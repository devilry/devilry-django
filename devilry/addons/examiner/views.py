from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count
from django.db.models import Q
from django.utils.simplejson import JSONEncoder
from django.core.urlresolvers import reverse
from django import http
from django.utils.translation import ugettext as _

from devilry.core.models import Delivery, AssignmentGroup, Assignment, Deadline
from devilry.core import gradeplugin
from devilry.core.utils.GroupNodes import group_assignments
from devilry.addons.dashboard import defaults

from django import forms
from devilry.ui.widgets import DevilryDateTimeWidget
from django.forms.models import inlineformset_factory, formset_factory
from devilry.ui.messages import UiMessages

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

@login_required
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    return render_to_response(
            'devilry/examiner/list_assignmentgroups.django.html', {
                'assignment_groups': assignment_groups,
                'assignment': assignment,
            }, context_instance=RequestContext(request))


@login_required
def delete_deadline(request, assignmentgroup_id, deadline_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_examiner(request.user):
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
    if not assignment_group.is_examiner(request.user):
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


@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_examiner(request.user):
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
        
    after_deadline = []
    within_a_deadline = []
    ungrouped_deliveries = []
    tmp_deliveries = []
    deadlines = assignment_group.deadlines.all().order_by('deadline')
    show_deadline_hint = False
    if deadlines.count() > 0:
        last_deadline = deadlines[deadlines.count()-1]
        after_deadline = assignment_group.deliveries.filter(
                time_of_delivery__gte = last_deadline)

        deliveries = []
        deadlineindex = 0
        deadline = deadlines[deadlineindex]
        deliveries_all = assignment_group.deliveries.filter(
                time_of_delivery__lt = last_deadline).order_by('time_of_delivery')
        for delivery in deliveries_all:
            if delivery.time_of_delivery > deadline.deadline:
                within_a_deadline.append((deadline, deliveries))
                deliveries = []
                deadlineindex += 1
                deadline = deadlines[deadlineindex]
            deliveries.insert(0, delivery)
        within_a_deadline.append((deadline, deliveries))

        # Adding deadlines that are left
        for i in xrange(deadlineindex+1, len(deadlines)):
            within_a_deadline.append((deadlines[i], list()))

        within_a_deadline.reverse()
    
        if len(within_a_deadline) > 0:
            tmp_deliveries.extend(list(within_a_deadline[0][1]))
    else:
        ungrouped_deliveries = assignment_group.deliveries.order_by('time_of_delivery')

    # Testing if any published deliveries on last deadline
    tmp_deliveries.extend(list(after_deadline))
    tmp_deliveries.extend(list(ungrouped_deliveries))
    for d in tmp_deliveries:
        if d.get_feedback().published:
            show_deadline_hint = True
            break
    if not assignment_group.is_open:
        show_deadline_hint = False

    messages = UiMessages()
    messages.load(request)
    
    return render_to_response(
            'devilry/examiner/show_assignmentgroup.django.html', {
                'assignment_group': assignment_group,
                'after_deadline': after_deadline,
                'within_a_deadline': within_a_deadline,
                'ungrouped_deliveries': ungrouped_deliveries,
                'deadline_form': deadline_form,
                'show_deadline_hint': show_deadline_hint,
                'messages': messages,
                'valid_deadlineform': valid_deadlineform
            }, context_instance=RequestContext(request))

@login_required
def correct_delivery(request, delivery_id):
    delivery_obj = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery_obj.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    key = delivery_obj.assignment_group.parentnode.grade_plugin
    return gradeplugin.registry.getitem(key).view(request, delivery_obj)

@login_required
def choose_assignment(request):
    assignments = Assignment.active_where_is_examiner(request.user)
    subjects = group_assignments(assignments)
    return render_to_response(
            'devilry/examiner/choose_assignment.django.html', {
                'subjects': subjects,
            }, context_instance=RequestContext(request))

@login_required
def assignmentgroup_filtertable_json(request):
    def latestdeliverytime(g):
        d = g.get_latest_delivery_with_feedback()
        if d:
            return d.time_of_delivery.strftime(defaults.DATETIME_FORMAT)
        else:
            return ""

    maximum = 20
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    groups = AssignmentGroup.where_is_examiner(request.user).order_by(
            'parentnode__parentnode__parentnode__short_name',
            'parentnode__parentnode__short_name',
            'parentnode__short_name',
            )
    if term != '':
        groups = groups.filter(
            Q(name__contains=term)
            | Q(parentnode__parentnode__parentnode__short_name__contains=term)
            | Q(parentnode__parentnode__short_name__contains=term)
            | Q(parentnode__short_name__contains=term)
            | Q(examiners__username__contains=term)
            | Q(candidates__student__username__contains=term))

    #if not request.GET.get('include_nodeliveries'):
        #groups = groups.exclude(Q(deliveries__isnull=True))
    #if not request.GET.get('include_corrected'):
        #groups = groups.annotate(
                #num_feedback=Count('deliveries__feedback')
                #).filter(num_feedback=0)

    groups = groups.distinct()
    allcount = groups.count()

    if showall != 'yes':
        groups = groups[:maximum]
    l = [dict(
            id = g.id,
            path = [
                g.parentnode.parentnode.parentnode.short_name,
                g.parentnode.parentnode.short_name,
                g.parentnode.short_name,
                str(g.id),
                g.get_candidates(),
                g.name or '',
                latestdeliverytime(g),
                g.get_status(),
            ],
            editurl = reverse('devilry-examiner-show_assignmentgroup',
                    args=[str(g.id)]))
        for g in groups]
    data = JSONEncoder().encode(dict(result=l, allcount=allcount))
    response = http.HttpResponse(data, content_type="text/plain")
    return response


