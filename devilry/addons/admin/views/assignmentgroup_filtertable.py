from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.db.models import Max

from devilry.core.models import AssignmentGroup
from devilry.ui.filtertable import (Filter, Action, FilterTable, Columns,
        Col, Row)


class FilterStatus(Filter):
    multiselect = True

    def get_labels(self, properties):
        l = []
        l.extend(AssignmentGroup.status_mapping)
        return l

    def filter(self, properties, dataset, selected):
        return dataset.filter(status__in=selected)

    def get_default_selected(self, properties):
        return [0, 1, 2, 3]


class FilterExaminer(Filter):

    def _get_examiners(self, properties):
        assignment = properties['assignment']
        examiners = User.objects.filter(examiners__parentnode=assignment).distinct()
        examiners = examiners.order_by('username')
        return examiners

    def get_labels(self, properties):
        examiners = self._get_examiners(properties)
        l = ["All", "No examiners"]
        l.extend([e.username for e in examiners])
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


class AssignmentGroupsFilterTable(FilterTable):
    id = 'assignmentgroups-admin-filtertable'
    filters = [
        FilterStatus('Status'),
        FilterExaminer('Examiners')
    ]
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
            ]
    relatedactions = [
            AssignmentGroupsAction(_("Create new"),
                "devilry-admin-create_assignmentgroup"),
            AssignmentGroupsAction(_("Create many (advanced)"),
                "devilry-admin-create_assignmentgroups"),
            AssignmentGroupsAction(_("Create by copy"),
                "devilry-admin-copy_groups")
            ]
    use_rowactions = True
    search_help = "Search the names of candidates on this group."
    #resultcount_supported = False

    def get_columns(self):
        return Columns(
            Col('candidates', "Candidates"),
            Col('examiners', "Examiners", optional=True, active_default=True),
            Col('name', "Name", can_order=True, optional=True,
                active_default=True),
            Col('deadlines', "Deadlines", optional=True),
            Col('active deadline', "Active deadline", optional=True),
            Col('latest delivery', "Latest delivery", optional=True),
            Col('deliveries', "Deliveries", optional=True),
            Col('status', "Status", can_order=True, optional=True,
                active_default=True))

    @classmethod
    def get_selected_groups(cls, request):
        groups = []
        for group_id in cls.get_selected_ids(request):
            group = get_object_or_404(AssignmentGroup, id=group_id)
            groups.append(group)
        return groups

    def __init__(self, request, assignment):
        super(AssignmentGroupsFilterTable, self).__init__(request)
        self.set_properties(assignment=assignment)
        self.assignment = assignment

    def create_row(self, group, active_optional_cols):
        candidates = group.get_candidates()
        row = Row(group.id, title=candidates)
        row.add_cell(candidates)

        if 'examiners' in active_optional_cols:
            row.add_cell(group.get_examiners())
        if 'name' in active_optional_cols:
            row.add_cell(group.name)
        if 'deadlines' in active_optional_cols:
            deadlines = "<br/>".join([unicode(deadline) for deadline in
                group.deadlines.all()])
            row.add_cell(deadlines)
        if 'active deadline' in active_optional_cols:
            deadline = group.get_active_deadline()
            row.add_cell(unicode(deadline))
        if 'latest delivery' in active_optional_cols:
            latest_delivery = group.deliveries.aggregate(
                    latest=Max("time_of_delivery")).get("latest")
            row.add_cell(unicode(latest_delivery or ""))
        if 'deliveries' in active_optional_cols:
            deliveries = group.deliveries.count()
            row.add_cell(unicode(deliveries))
        if 'status' in active_optional_cols:
            row.add_cell(group.get_localized_status(),
                    cssclass=group.get_status_cssclass())

        row.add_action(_("edit"), 
                reverse('devilry-admin-edit_assignmentgroup',
                        args=[self.assignment.id, str(group.id)]))
        row.add_action(_("examine"), 
                reverse('devilry-examiner-show_assignmentgroup',
                        args=[str(group.id)]))
        return row

    def create_dataset(self):
        dataset = self.assignment.assignmentgroups.all()
        total = self.assignment.assignmentgroups.all().count()
        return total, dataset

    def get_dataset_size(self, dataset):
        return dataset.count()

    def limit_dataset(self, dataset, start, end):
        return dataset[start:end]

    def order_by(self, dataset, colnum, order_asc):
        prefix = '-'
        if order_asc:
            prefix = ''
        if colnum == 2:
            key = 'name'
        else:
            key = 'status'
        return dataset.order_by(prefix + key)

    def search(self, dataset, qry):
        return dataset.filter(
                candidates__student__username__contains=qry)
