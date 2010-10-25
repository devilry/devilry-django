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
    def __init__(self, id, cssclass="", title=""):
        self.id = id
        self.title = title
        self.cells = []
        self.cssclass = cssclass
        self.actions = []

    def add_cell(self, value, cssclass=""):
        self.cells.append(Cell(value, cssclass))

    def add_action(self, label, url):
        self.actions.append({"label": label, "url":url})

    def as_dict(self):
        return dict(
            id = self.id,
            title = self.title,
            cells = [c.as_dict() for c in self.cells],
            cssclass = self.cssclass,
            actions = self.actions
        )

    def __getitem__(self, index):
        return self.cells[index]


class Columns(dict):
    def __init__(self, *cols):
        self.lst = cols
        for col in cols:
            self[col.id] = col

    def get_by_index(self, index):
        return self.lst[index]

    def iter_ordered(self):
        return self.lst.__iter__()

class Col(object):
    def __init__(self, id, title, can_order=False, optional=False,
            active_default=False):
        self.id = id
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
    confirm_title = None
    confirm_message = None
    url = None

    def __init__(self, label, url, confirm_title=None,
            confirm_message=None):
        self.label = label
        self.url = url
        self.confirm_title = confirm_title
        self.confirm_message = confirm_message

    def as_dict(self, properties):
        d = dict(label=self.label, url=self.get_url(properties),
                cssclasses=self.cssclasses,
                confirm_title=self.confirm_title,
                confirm_message=self.confirm_message)
        return d

    def get_url(self, properties):
        return self.url


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
    selectionactions = []
    relatedactions = []
    resultcount_supported = True
    search_help = ""

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'id': cls.id,
            'jsonurl': jsonurl,
            'search_help': cls.search_help,
            'has_selection_actions': len(cls.selectionactions) > 0,
            'has_related_actions':  len(cls.relatedactions) > 0,
            'has_search': hasattr(cls, "search"),
            'has_filters': len(cls.filters) > 0,
            'resultcount_supported': cls.resultcount_supported
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
        self.columns = self.get_columns()
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
            set([c.id for c in self.columns.itervalues()
                if c.optional and c.active_default]))
        return default_session

    def session_from_indata(self):
        indata = self.indata
        default_session = self.get_default_session()
        if "reset" in indata:
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
            perpage = indata["perpage"]
            if perpage == "all":
                self.session.perpage = "all"
            else:
                self.session.perpage = toint(indata["perpage"],
                        self.default_perpage)
        if "search" in indata:
            self.session.search = indata["search"]
        if "active_cols" in indata:
            if indata['active_cols'] == "none":
                cols = []
            else:
                cols = set()
                for i in indata.getlist("active_cols"):
                    colnum = int(i)
                    col = self.columns.get_by_index(colnum)
                    if col.optional:
                        cols.add(col.id)
            self.session.active_optional_columns = cols

        if "order_by" in indata:
            i = int(indata["order_by"])
            if i == self.session.order_by:
                self.session.order_asc = not self.session.order_asc
            else:
                self.session.order_asc = True
                self.session.order_by = self.columns.get_by_index(i).id

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

    #def search(self, dataset, qry):
        #raise NotImplementedError()

    def get_columns(self):
        return Columns()

    def get_dataset_size(self, dataset):
        return dataset.count()

    def limit_dataset(self, dataset, start, end):
        return dataset[start:end]

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
        return [col.as_dict() for col in self.columns.iter_ordered()
                if not col.optional
                    or col.id in self.session.active_optional_columns]

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

        if self.session.perpage == "all":
            start = 0
            end = totalsize
        else:
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

        if self.session.perpage == "all":
            perpage_js = totalsize
        else:
            perpage_js = self.session.perpage
        out = dict(
            totalsize = totalsize,
            filteredsize = filteredsize,
            currentpage = self.session.currentpage,
            perpage = perpage_js,
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
                    'is_active': c.id in self.session.active_optional_columns}
                for c in self.columns.iter_ordered()],
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
