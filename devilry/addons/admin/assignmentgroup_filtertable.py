"""
Base functionality for a :class:`devilry.ui.filtertable.FilterTable` for
AssignmentGroups.
"""
from datetime import datetime
from django.template import RequestContext
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models import Max, Min, Count, Q, F
from django.utils.formats import date_format
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
        HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404

from devilry.ui.messages import UiMessages
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryMultiSelectFewCandidates
from devilry.addons.quickdash import defaults
from devilry.core.models import (AssignmentGroup, Candidate, Assignment,
        Deadline)
from devilry.ui.filtertable import (Filter, Action, FilterTable,
        Row, FilterLabel)


class FilterStatus(Filter):
    title = _("Status")
    multiselect = True

    def get_labels(self, properties):
        l = []
        l.extend([FilterLabel(s) for s in AssignmentGroup.status_mapping])
        return l

    def filter(self, properties, dataset, selected):
        return dataset.filter(status__in=selected)

    def get_default_selected(self, properties):
        return [0, 1, 2, 3]


class FilterIsPassingGrade(Filter):
    title = _("Is passing grade?")

    def get_labels(self, properties):
        return [FilterLabel.DEFAULT,
                FilterLabel(_("Yes")),
                FilterLabel(_("No"))]

    def filter(self, properties, dataset, selected):
        i = selected[0]
        if i == 0:
            return dataset
        else:
            return dataset.filter(is_passing_grade=(i==1))

class FilterNumberOfCandidates(Filter):
    title = _("Number of candidates")

    def __init__(self, assignment):
        qry = assignment.assignmentgroups.annotate(
                num_candidates=Count("candidates")).aggregate(
                        minimum=Min("num_candidates"),
                        maximum=Max("num_candidates"))
        self.minimum = qry['minimum'] or 0
        self.maximum = qry['maximum'] or 0

    def get_labels(self, properties):
        l = [FilterLabel.DEFAULT,
            FilterLabel(_("More than 0"))]
        l.extend([FilterLabel(n) for n in xrange(self.maximum+1)])
        return l

    def filter(self, properties, dataset, selected):
        i = selected[0] - 2
        if i == -2:
            return dataset
        if i == -1:
            return dataset.annotate(
                    num_candidates=Count("candidates")).filter(
                            num_candidates__gt=0)
        else:
            return dataset.annotate(
                    num_candidates=Count("candidates")).filter(
                            num_candidates=i)

class FilterMissingCandidateId(Filter):
    title = _("Missing candidate id's?")

    def get_labels(self, properties):
        return [FilterLabel.DEFAULT,
                FilterLabel(_("Yes"),
                    _("Matches any group where at least one member is "\
                        "without a candidate number.")),
                FilterLabel(_("No"),
                    _("Matches any group where no member is "\
                        "without a candidate number.")),
                ]

    def filter(self, properties, dataset, selected):
        s = selected[0]
        if s == 0:
            return dataset
        assignment = properties['assignment']
        missing_id = Candidate.objects.filter(
                Q(assignment_group__parentnode = assignment) &
                (Q(candidate_id="")|Q(candidate_id__isnull=True)))
        if s == 1:
            return dataset.filter(
                    candidates__id__in=missing_id)
        if s == 2:
            return dataset.exclude(
                    candidates__id__in=missing_id)
        return dataset


class FilterExaminer(Filter):
    title = _("Examiners")

    def _get_examiners(self, properties):
        assignment = properties['assignment']
        examiners = User.objects.filter(examiners__parentnode=assignment).distinct()
        examiners = examiners.order_by('username')
        return examiners

    def get_labels(self, properties):
        examiners = self._get_examiners(properties)
        l = [FilterLabel.DEFAULT, FilterLabel(_("No examiners"))]
        l.extend([FilterLabel(e.username) for e in examiners])
        return l

    def filter(self, properties, dataset, selected):
        examiners = self._get_examiners(properties)
        i = selected[0] - 2
        if i == -2:
            return dataset
        elif i == -1:
            return dataset.filter(examiners__isnull=True)
        else:
            selected = examiners[i]
            return dataset.filter(examiners=selected)


class FilterAfterDeadline(Filter):
    title = _("After deadline")

    def get_labels(self, properties):
        return [FilterLabel.DEFAULT,
                FilterLabel(_("Latest delivery"),
                    _("Show groups where latest delivery is after the deadline.")),
                FilterLabel(_("None after deadline"),
                    _("Show groups with no deliveries after the deadline."))]

    def filter(self, properties, dataset, selected):
        i = selected[0]
        if i == 1:
            return dataset.filter(
                    latest_delivery__gt=F("active_deadline"))
        elif i == 2:
            return dataset.filter(
                    latest_delivery__lte=F("active_deadline"))
        else:
            return dataset


class AssignmentGroupsAction(Action):
    def __init__(self, label, urlname, confirm_title=None,
            confirm_message=None):
        self.label = label
        self.urlname = urlname
        self.confirm_title = confirm_title
        self.confirm_message = confirm_message

    def get_url(self, properties):
        assignment = properties['assignment']
        return reverse(self.urlname, args=[str(assignment.id)])


def _datetime_or_empty(datetimeobj):
    if datetimeobj:
        return date_format(datetimeobj, "DATETIME_FORMAT")
    else:
        return ""


class AssignmentGroupsFilterTableBase(FilterTable):
    resultcount_supported = True
    use_rowactions = True
    search_help = _("Search the names of candidates on this group.")

    @classmethod
    def get_selected_groups(cls, request):
        """ Get a list of selected
        :class:`devilry.core.models.AssignmentGroup`. """
        groups = []
        for group_id in cls.get_selected_ids(request):
            group = get_object_or_404(AssignmentGroup, id=group_id)
            groups.append(group)
        return groups

    @classmethod
    def get_selected_nodes(cls, request):
        """ Alias for get_selected_groups to make this work with
        deletemany_generic. """
        return cls.get_selected_groups(request)

    def __init__(self, request, assignment):
        self.assignment = assignment
        super(AssignmentGroupsFilterTableBase, self).__init__(request,
                assignment=assignment)

    def create_row(self, group, active_optional_cols):
        candidates = group.get_candidates()
        row = Row(group.id, title=candidates)
        if 'id' in active_optional_cols:
            row.add_cell(group.pk)
        row.add_cell(candidates)
        if 'examiners' in active_optional_cols:
            row.add_cell(group.get_examiners())
        if 'name' in active_optional_cols:
            row.add_cell(group.name or "")
        if 'deadlines' in active_optional_cols:
            deadlines = "<br/>".join([unicode(deadline) for deadline in
                group.deadlines.all()])
            row.add_cell(deadlines)

        if 'latest_delivery' in active_optional_cols \
                or 'active_deadline' in active_optional_cols:
            # Avoid calculating active_deadline twice
            active_deadline = group.get_active_deadline()
            if 'active_deadline' in active_optional_cols:
                if active_deadline:
                    row.add_cell(_datetime_or_empty(active_deadline.deadline))
                else:
                    row.add_cell("")
            if 'latest_delivery' in active_optional_cols:
                cssclass = ""
                if group.latest_delivery and active_deadline and active_deadline.deadline < group.latest_delivery:
                    cssclass = "bad"
                row.add_cell(_datetime_or_empty(group.latest_delivery),
                        cssclass=cssclass)

        if 'deliveries_count' in active_optional_cols:
            row.add_cell(group.deliveries_count)
        if 'scaled_points' in active_optional_cols:
            row.add_cell("%.2f/%d" % (group.scaled_points,
                self.assignment.pointscale))
        if 'grade' in active_optional_cols:
            row.add_cell(group.get_grade_as_short_string() or "")
        if 'status' in active_optional_cols:
            row.add_cell(group.get_localized_status(),
                    cssclass=group.get_status_cssclass())
        return row

    def search(self, dataset, qry):
        if self.assignment.anonymous:
            dataset = dataset.filter(
                candidates__candidate_id=qry)
        else:
            dataset = dataset.filter(
                candidates__student__username__contains=qry)
        return dataset


    def get_assignmentgroups(self):
        raise NotImplementedError()

    def create_dataset(self):
        dataset = self.get_assignmentgroups().distinct()
        total = dataset.count()
        dataset = dataset.annotate(
                active_deadline=Max('deadlines__deadline'),
                latest_delivery=Max("deliveries__time_of_delivery"),
                deliveries_count=Count("deliveries"))
        return total, dataset


class DeadlineForm(forms.ModelForm):
    """ Deadline form used for standalone. """
    class Meta:
        model = Deadline
        fields = ["deadline", "text"]
        widgets = {
                'deadline': DevilryDateTimeWidget,
                'text': forms.Textarea(attrs=dict(rows=12, cols=70))
                }


def create_deadline_base(request, assignment_id, groups, checkbox_name):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    assignment = get_object_or_404(Assignment, id=assignment_id)
    isAdmin = assignment.can_save(request.user)

    if not isAdmin:
        for group in groups:
            if not group.is_examiner(request.user):
                return HttpResponseForbidden("Forbidden")

    datetimefullformat = '%Y-%m-%d %H:%M:%S'
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
        deadline = Deadline(assignment_group=groups[0])
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
            for group in groups:
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
            'checkbox_name': checkbox_name
            }, context_instance=RequestContext(request))


def clear_deadlines_base(request, assignment_id, groups):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    if request.method == 'POST':
        ids = [g.id for g in groups]
        selected_deadlines = Deadline.objects.filter(
                assignment_group__in=ids)
        for d in selected_deadlines:
            d.delete()
        messages = UiMessages()
        messages.add_success(
                _('Deadlines successfully cleared from: %(groups)s.' %
                {'groups': ', '.join([str(g) for g in groups])}))
        messages.save(request)
        return HttpResponseRedirect(reverse(
            'devilry-admin-edit_assignment',
            args=[assignment_id]))
    else:
        return HttpResponseBadRequest()
