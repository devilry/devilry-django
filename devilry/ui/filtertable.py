from django.utils.translation import ugettext as _
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
    def __init__(self, title, can_order=False, optional=False,
            active_default=False):
        self.title = title
        self.can_order = can_order
        self.optional = optional
        self.active_default = active_default

    def as_dict(self):
        return dict(can_order=self.can_order, title=self.title,
                optional=self.optional, active_default=self.active_default)


class Filter(object):
    """
    .. attribute:: multiselect

        Is the filter multiselect or not? If it is multiselect, the user can
        choose more than one label at one time.
    """
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
                labels = labels)

    def get_selected(self, current, selected, properties):
        """
        :param current: A list with indexes of the currently selected items.
        :param selected: The index of the selected label.
        :return:
            A list with the index of selected items. If this filter is not
            :attr:`multiselect`, only the first item in the list is used.
        """
        if self.multiselect:
            if selected in current:
                current.remove(selected)
            else:
                current.append(selected)
            return current
        else:
            return [selected]

    def get_default_selected(self, properties):
        """ A list of the index of the labels that are selected by default.
        If this filter is not :attr:`multiselect`, only the first item in
        the list is used. """
        return [0]

    def get_all_selected(self, properties):
        return range(len(self.get_labels(properties)))

    def get_all_unselected(self, properties):
        return []


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
            default_order_by, default_order_asc, default_filters,
            default_active_optional_columns):
        self.search = ""
        self.order_by = default_order_by
        self.order_asc = default_order_asc
        self.filters = default_filters
        self.currentpage = default_currentpage
        self.perpage = default_perpage
        self.active_optional_columns = default_active_optional_columns
        print self.active_optional_columns

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
    resultcount_supported = True

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'id': cls.id,
            'jsonurl': jsonurl,
            'resultcount_supported': str(cls.resultcount_supported).lower()
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
        self.indata = request.GET
        self.session_from_indata()
        #del self.request.session[self.id]
        
    def get_default_session(self):
        default_filters = {}
        for i, f in enumerate(self.filters):
            default_filters[i] = f.get_default_selected(self.properties)
        default_session = SessionInfo(
            self.default_currentpage, self.default_perpage,
            self.default_order_by, self.default_order_asc,
            default_filters,
            [i for i, c in enumerate(self.columns)
                if c.optional and c.active_default])
        return default_session

    def session_from_indata(self):
        indata = self.indata
        default_session = self.get_default_session()
        if "reset_filters" in indata:
            self.session = default_session
            return
        self.session = self.request.session.get(self.id, default_session)

        def toint(s, default):
            try:
                return int(s)
            except:
                return default
        if "gotopage" in indata:
            self.session.currentpage = toint(indata["gotopage"], 0)
        if "perpage" in indata:
            self.session.perpage = toint(indata["perpage"],
                    self.default_perpage)
        if "search" in indata:
            self.session.search = indata["search"]
        if "active_cols" in indata:
            if indata['active_cols'] == "none":
                cols = []
            else:
                not_optional = [i for i, c in enumerate(self.columns)
                        if not c.optional]
                cols = [int(colnum)
                        for colnum in indata.getlist("active_cols")
                        if not int(colnum) in not_optional]
            self.session.active_optional_columns = cols
        print self.session.active_optional_columns

        if "order_by" in indata:
            i = int(indata["order_by"])
            if i == self.session.order_by:
                self.session.order_asc = not self.session.order_asc
            else:
                self.session.order_asc = True
                self.session.order_by = i

        checkall_in_filter = int(indata.get("checkall_in_filter", -1))
        for i, f in enumerate(self.filters):
            current = self.session.filters[i]
            if i == checkall_in_filter:
                allselected = f.get_all_selected(self.properties)
                if len(current) == len(allselected):
                    value = f.get_all_unselected(self.properties)
                else:
                    value = allselected
            else:
                selectedkey = "filter_selected_%s" % i
                if selectedkey in indata:
                    selected = int(indata[selectedkey])
                    value = f.get_selected(current, selected,
                            self.properties)
                else:
                    value = current
            self.session.filters[i] = value
                

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
        """ Get a list containing a dictionary for each filter. The
        dictionary is created with :meth:`Filter.as_dict`.

        :param dataset:
            The **unfiltered** dataset returned by :meth:`create_dataset`.
        """
        return [f.as_dict(self.properties, dataset, self.session.filters[i])
                for i, f in enumerate(self.filters)]

    def filter(self, dataset):
        for i, selected in self.session.filters.iteritems():
            dataset = self.filters[i].filter(self.properties,
                    dataset, selected)
        return dataset

    def search_and_filter(self, dataset):
        """ Search and filter the given dataset.

        :return: (dataset, filteredsize) where ``dataset`` is the searched
            and filtered dataset, and ``filteredsize`` is the size of the
            dataset.
        """
        if self.session.search:
            dataset = self.search(dataset, self.session.search)
        dataset = self.filter(dataset)
        filteredsize = self.get_dataset_size(dataset)
        return dataset, filteredsize

    def get_active_columns(self):
        return [col.as_dict() for i, col in enumerate(self.columns)
                if not col.optional
                    or i in self.session.active_optional_columns]

    def dataset_to_rowlist(self, dataset):
        return [self.create_row(d,
            self.session.active_optional_columns).as_dict() for d in dataset]

    def create_jsondata(self):
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset, filteredsize = self.search_and_filter(dataset)

        if self.session.order_by != None:
            dataset = self.order_by(dataset, self.session.order_by,
                    self.session.order_asc)

        start = self.session.currentpage*self.session.perpage
        end = start + self.session.perpage
        if start > filteredsize:
            start = 0
            self.session.currentpage = 0

        dataset = self.limit_dataset(dataset, start, end)
        rowlist = self.dataset_to_rowlist(dataset)

        if self.session.search:
            statusmsg = _("Current filters, including the search for "\
                    "<strong>%(search)s</strong>, match %(filteredsize)d of "\
                    "%(totalsize)d available items.")
        else:
            statusmsg = _("Current filters match %(filteredsize)d of "\
                    "%(totalsize)d available items.")
        statusmsg = statusmsg % dict(
                search = self.session.search,
                filteredsize = filteredsize,
                totalsize = totalsize)

        out = dict(
            totalsize = totalsize,
            filteredsize = filteredsize,
            currentpage = self.session.currentpage,
            perpage = self.session.perpage,
            search = self.session.search,
            filterview = filterview,
            columns = self.get_active_columns(),
            use_rowactions = self.use_rowactions,
            selectionactions = self.get_selectionactions_as_dicts(),
            relatedactions = self.get_relatedactions_as_dicts(),
            order_by = self.session.order_by,
            order_asc = self.session.order_asc,
            data = rowlist,
            all_columns = [{
                    'col':c.as_dict(),
                    'is_active': i in self.session.active_optional_columns}
                for i, c in enumerate(self.columns)],
            statusmsg = statusmsg
        )
        #print "Session:"
        #print self.session
        self.save_session()
        return out

    def save_session(self):
        self.request.session[self.id] = self.session

    def create_json_count(self):
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset, filteredsize = self.search_and_filter(dataset)
        return dict(filteredsize=filteredsize)

    def json_response(self):
        if "countonly" in self.indata:
            out = self.create_json_count()
        else:
            out = self.create_jsondata()
        json = JSONEncoder(ensure_ascii=False, indent=4).encode(out)
        return HttpResponse(json, content_type="text/plain")
