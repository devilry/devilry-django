from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from devilry.core.models import AssignmentGroup
from devilry.ui.filtertable import Filter, Action, FilterTable, Col, Row


class FilterStatus(Filter):
    multiselect = True

    def get_labels(self, properties):
        l = ["All"]
        l.extend(AssignmentGroup.status_mapping)
        return l

    def filter(self, properties, dataset, selected):
        status = selected[0] - 1
        if status == -1:
            return dataset
        else:
            return dataset.filter(status=status)


class FilterExaminer(Filter):

    def _get_examiners(self, properties):
        assignment = properties['assignment']
        examiners = User.objects.filter(examiners__parentnode=assignment).distinct()
        examiners.order_by('username')
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
    def __init__(self, label, urlname):
        self.label = label
        self.urlname = urlname

    def get_url(self, properties):
        assignment = properties['assignment']
        return reverse(self.urlname, args=[str(assignment.id)])


class AssignmentGroupsFilterTable(FilterTable):
    filters = [
        FilterStatus('Status'),
        FilterExaminer('Examiners')
    ]
    columns = [Col("Candidates"), Col("Examiners"),
            Col("Name", can_order=True),
            Col("Status", can_order=True)]
    selectionactions = [
            AssignmentGroupsAction(_("Create/replace deadline"),
                'devilry-admin-create_deadline'),
            AssignmentGroupsAction(_("Set examiners"),
                'devilry-admin-set_examiners')
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

    def create_row(self, group):
        cells = [group.get_candidates(), group.get_examiners(),
                group.name, group.get_localized_status()]
        row = Row(group.id, cells)
        row[3].cssclass = group.get_status_cssclass()
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
