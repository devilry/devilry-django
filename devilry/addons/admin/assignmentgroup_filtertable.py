"""
Base functionality for a :class:`devilry.ui.filtertable.FilterTable` for
AssignmentGroups.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.db.models import Max, Min, Count, Q
from django.utils.formats import date_format

from devilry.core.models import AssignmentGroup, Candidate
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
        return [FilterLabel(_("All")), FilterLabel(_("Yes")),
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
        l = [FilterLabel(_("All")), FilterLabel(_("More than 0"))]
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
        return [FilterLabel(_("All")),
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
        l = [FilterLabel(_("All")), FilterLabel(_("No examiners"))]
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
        if 'active_deadline' in active_optional_cols:
            deadline = group.get_active_deadline()
            row.add_cell(_datetime_or_empty(deadline.deadline))
        if 'latest_delivery' in active_optional_cols:
            row.add_cell(_datetime_or_empty(group.latest_delivery))
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
                latest_delivery=Max("deliveries__time_of_delivery"),
                deliveries_count=Count("deliveries"))
        return total, dataset

