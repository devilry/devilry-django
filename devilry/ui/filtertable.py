from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.simplejson import JSONEncoder
from django.http import HttpResponse


class Row(object):
    def __init__(self, cells, cssclass=None):
        self.cells = cells
        self.cssclass = cssclass
        self.actions = []

    def add_action(self, label, url):
        self.actions.append({"label": label, "url":url})

    def as_dict(self):
        return dict(
            cells = self.cells,
            cssclass = self.cssclass,
            actions = self.actions
        )


class Col(object):
    def __init__(self, title, can_order=False):
        self.title = title
        self.can_order = can_order

    def as_dict(self):
        return dict(can_order=self.can_order, title=self.title)


class Filter(object):
    multiselect = False

    def __init__(self, title):
        self.title = title

    def get_labels(self, properties):
        return ["All"]

    def filter(self, properties, dataset, selected):
        return dataset

    def as_dict(self, properties, dataset, selected):
        labels = [{
            'selected': i in selected,
            'label': label}
            for i, label in enumerate(self.get_labels(properties))]
        return dict(
                title = self.title,
                multiselect = self.multiselect,
                selected = selected,
                labels = labels)

    def get_selected(self, current, selected):
        if selected == None:
            return current
        else:
            return [selected]


class SessionInfo(object):
    def __init__(self):
        self.search = None
        self.order_by = None
        self.order_asc = False
        self.filters = {}

class FilterTable(object):
    id = 'filtertable'
    default_perpage = 20
    filters = []
    columns = []

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'id': cls.id,
            'jsonurl': jsonurl
            }, context_instance=RequestContext(request))

    def __init__(self, request):
        self.properties = {}
        indata = request.GET
        self.start = int(indata.get("start", 0))
        self.perpage = int(indata.get("perpage", self.default_perpage))
        self.session = request.session.get(self.id, SessionInfo())

        if "order_by" in indata:
            i = int(indata["order_by"])
            if i == self.session.order_by:
                self.session.order_asc = not self.session.order_asc
            else:
                self.session.order_asc = True
                self.session.order_by = i

        for i, f in enumerate(self.filters):
            key = "filter_selected_%s" % i
            selected = None
            if key in indata:
                selected = int(indata[key])
            current = self.session.filters.get(i, [0])
            self.session.filters[i] = f.get_selected(current, selected)

        request.session[self.id] = self.session
        print "Session:", self.session.filters


    def create_row(self, group):
        raise NotImplementedError()

    def create_dataset(self):
        raise NotImplementedError()


    def order_by(self, dataset, colnum):
        return dataset

    def set_properties(self, **properties):
        self.properties.update(properties)

    def create_filterview(self, dataset):
        return [f.as_dict(self.properties, dataset, self.session.filters[i])
                for i, f in enumerate(self.filters)]

    def filter(self, dataset):
        for i, selected in self.session.filters.iteritems():
            dataset = self.filters[i].filter(self.properties,
                    dataset, selected)
        return dataset

    def limit_dataset(self, dataset, start, perpage):
        pass

    def dataset_to_rowlist(self, dataset):
        return [self.create_row(d).as_dict() for d in dataset]

    def create_jsondata(self):
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset = self.filter(dataset)
        if self.session.order_by != None:
            dataset = self.order_by(dataset, self.session.order_by,
                    self.session.order_asc)
        dataset = self.limit_dataset(dataset, self.start, self.perpage)
        out = dict(
            total = totalsize,
            filterview = filterview,
            columns = [c.as_dict() for c in self.columns],
            data = self.dataset_to_rowlist(dataset)
        )
        return out

    def json_response(self):
        json = JSONEncoder(ensure_ascii=False, indent=4).encode(
                self.create_jsondata())
        return HttpResponse(json, content_type="text/plain")





from devilry.core.models import AssignmentGroup
from django.contrib.auth.models import User


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


class AssignmentGroupsFilterTable(FilterTable):
    filters = [
        FilterStatus('Status'),
        FilterExaminer('Examiners')
    ]
    columns = [Col("Candidates"), Col("Examiners"), Col("Name"),
            Col("Status", can_order=True)]

    def __init__(self, request, assignment):
        super(AssignmentGroupsFilterTable, self).__init__(request)
        self.set_properties(assignment=assignment)
        self.assignment = assignment

    def create_row(self, group):
        cells = [group.get_candidates(), group.get_examiners(),
                group.name, group.get_localized_status()]
        row = Row(cells)
        return row

    def create_dataset(self):
        dataset = self.assignment.assignmentgroups.all()
        total = self.assignment.assignmentgroups.all().count()
        return total, dataset

    def limit_dataset(self, dataset, start, perpage):
        return dataset[start:perpage]

    def order_by(self, dataset, colnum, order_asc):
        prefix = '-'
        if order_asc:
            prefix = ''
        return dataset.order_by(prefix + 'status')
