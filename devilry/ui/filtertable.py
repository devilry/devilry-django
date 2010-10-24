from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.simplejson import JSONEncoder
from django.http import HttpResponse


class Cell(object):
    def __init__(self, value, cssclass=""):
        self.value = value
        self.cssclass = cssclass

    def as_dict(self):
        return dict(value=self.value, cssclass=self.cssclass)


class Row(object):
    def __init__(self, id, cells, cssclass=[]):
        self.id = id
        self.cells = [Cell(c) for c in cells]
        self.cssclass = cssclass
        self.actions = []

    def add_action(self, label, url):
        self.actions.append({"label": label, "url":url})

    def as_dict(self):
        return dict(
            id = self.id,
            cells = [c.as_dict() for c in self.cells],
            cssclass = self.cssclass,
            actions = self.actions
        )

    def __getitem__(self, index):
        return self.cells[index]


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


class Confirm(object):
    def __init__(self, title, buttonlabel, confirm_message=None):
        self.title = title
        self.buttonlabel = buttonlabel
        self.confirm_message = confirm_message

    def as_dict(self):
        return dict(title=self.title, buttonlabel=self.buttonlabel,
                confirm_message=self.confirm_message)

class Action(object):
    label = None
    cssclasses = []

    def as_dict(self, properties):
        d = dict(label=self.label, url=self.get_url(properties),
                cssclasses=self.cssclasses)
        return d

    def get_confirm_message(self, properties):
        return None

    def get_url(self, properties):
        raise NotImplementedError()


class SessionInfo(object):
    def __init__(self, default_currentpage, default_perpage,
            default_order_by, default_order_asc):
        self.search = ""
        self.order_by = default_order_by
        self.order_asc = default_order_asc
        self.filters = {}
        self.currentpage = default_currentpage
        self.perpage = default_perpage

    def __str__(self):
        return "\n".join(["   %s:%s" % (k, v)
            for k, v in self.__dict__.iteritems()
            if not k.startswith("_")])


class FilterTable(object):
    id = 'filtertable'
    default_currentpage = 0
    default_perpage = 10
    default_order_by = None
    default_order_asc = False
    use_rowactions = False
    filters = []
    columns = []
    selectionactions = []
    relatedactions = []

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'id': cls.id,
            'jsonurl': jsonurl
            }, context_instance=RequestContext(request))

    @classmethod
    def get_checkbox_name(cls):
        return '%s-checkbox' % cls.id

    @classmethod
    def get_selected_ids(cls, request):
        return request.POST.getlist(cls.get_checkbox_name())

    def __init__(self, request):
        self.properties = {}
        self.request = request
        self.session = request.session.get(self.id, SessionInfo(
            self.default_currentpage, self.default_perpage,
            self.default_order_by, self.default_order_asc))
        

    def session_from_indata(self):
        indata = self.request.GET
        if "gotopage" in indata:
            self.session.currentpage = int(indata["gotopage"])
        if "perpage" in indata:
            self.session.perpage = int(indata["perpage"])
        if "search" in indata:
            self.session.search = indata["search"]

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

    def create_row(self, group):
        raise NotImplementedError()

    def create_dataset(self):
        raise NotImplementedError()

    def limit_dataset(self, dataset, currentpage, perpage):
        raise NotImplementedError()

    def search(self, dataset, qry):
        raise NotImplementedError()

    def get_selectionactions_as_dicts(self):
        return [a.as_dict(self.properties) for a in self.selectionactions]
    def get_relatedactions_as_dicts(self):
        return [a.as_dict(self.properties) for a in self.relatedactions]

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

    def dataset_to_rowlist(self, dataset):
        return [self.create_row(d).as_dict() for d in dataset]

    def create_jsondata(self):
        self.session_from_indata()
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset = self.search(dataset, self.session.search)
        dataset = self.filter(dataset)
        if self.session.order_by != None:
            dataset = self.order_by(dataset, self.session.order_by,
                    self.session.order_asc)

        filteredsize = self.get_dataset_size(dataset)
        start = self.session.currentpage*self.session.perpage
        end = start + self.session.perpage
        if start > filteredsize:
            start = 0
            self.session.currentpage = 0

        dataset = self.limit_dataset(dataset, start, end)
        rowlist = self.dataset_to_rowlist(dataset)
        out = dict(
            totalsize = totalsize,
            filteredsize = filteredsize,
            currentpage = self.session.currentpage,
            perpage = self.session.perpage,
            search = self.session.search,
            filterview = filterview,
            columns = [c.as_dict() for c in self.columns],
            use_rowactions = self.use_rowactions,
            selectionactions = self.get_selectionactions_as_dicts(),
            relatedactions = self.get_relatedactions_as_dicts(),
            order_by = self.session.order_by,
            order_asc = self.session.order_asc,
            data = rowlist
        )
        print "Session:"
        print self.session
        self.request.session[self.id] = self.session
        return out

    def json_response(self):
        json = JSONEncoder(ensure_ascii=False, indent=4).encode(
                self.create_jsondata())
        return HttpResponse(json, content_type="text/plain")
