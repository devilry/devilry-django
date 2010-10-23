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


class Filter(object):
    multiselect = False

    def __init__(self, title):
        self.title = title

    def getlabels(self):
        return []

    def filter(self, dataset, selected):
        return dataset

    def as_dict(self, dataset, selected):
        labels = [{
            'selected': i in selected,
            'label': label}
            for i, label in enumerate(self.getlabels())]
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


from devilry.core.models import AssignmentGroup
class FilterStatus(Filter):
    multiselect = True

    def getlabels(self):
        l = ["All"]
        l.extend(AssignmentGroup.status_mapping)
        return l

    def filter(self, dataset, selected):
        status = selected[0] - 1
        if status == -1:
            return dataset
        else:
            return dataset.filter(status=status)


class SessionInfo(object):
    def __init__(self):
        self.search = None
        self.filters = {}

class FilterTable(object):
    id = 'filtertable'
    default_perpage = 20
    filters = []

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'columns': cls.get_columns(),
            'id': cls.id,
            'jsonurl': jsonurl
            }, context_instance=RequestContext(request))

    @classmethod
    def get_columns(cls):
        return []

    def __init__(self, request):
        self.properties = request.GET
        self.start = int(self.properties.get("start", 0))
        self.perpage = int(self.properties.get("perpage", self.default_perpage))

        self.session = request.session.get(self.id, SessionInfo())
        for i, f in enumerate(self.filters):
            key = "filter_selected_%s" % i
            selected = None
            if key in self.properties:
                selected = int(self.properties[key])
            current = self.session.filters.get(i, 0)
            self.session.filters[i] = f.get_selected(current, selected)

        request.session[self.id] = self.session
        print "Session:", self.session.filters


    def create_row(self, group):
        raise NotImplementedError()

    def create_dataset(self):
        raise NotImplementedError()

    def create_filterview(self, dataset):
        return [f.as_dict(dataset, self.session.filters[i])
                for i, f in enumerate(self.filters)]

    def filter(self, dataset):
        for i, selected in self.session.filters.iteritems():
            dataset = self.filters[i].filter(dataset, selected)
        return dataset

    def limit_dataset(self, dataset, start, perpage):
        pass

    def dataset_to_rowlist(self, dataset):
        return [self.create_row(d).as_dict() for d in dataset]

    def create_jsondata(self):
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset = self.filter(dataset)
        dataset = self.limit_dataset(dataset, self.start, self.perpage)
        out = dict(
            total = totalsize,
            filterview = filterview,
            data = self.dataset_to_rowlist(dataset)
        )
        return out

    def json_response(self):
        json = JSONEncoder(ensure_ascii=False, indent=4).encode(
                self.create_jsondata())
        return HttpResponse(json, content_type="text/plain")


class AssignmentGroupsFilterTable(FilterTable):

    filters = [
        FilterStatus('Status')
    ]

    @classmethod
    def get_columns(cls):
        return ["Candidates", "Examiners", "Name"]

    def __init__(self, request, assignment):
        super(AssignmentGroupsFilterTable, self).__init__(request)
        self.assignment = assignment

    def create_row(self, group):
        cells = [group.get_candidates(), group.get_examiners(),
                group.name]
        row = Row(cells)
        return row

    def create_dataset(self):
        dataset = self.assignment.assignmentgroups.all()
        total = self.assignment.assignmentgroups.all().count()
        return total, dataset

    def limit_dataset(self, dataset, start, perpage):
        return dataset[start:perpage]
