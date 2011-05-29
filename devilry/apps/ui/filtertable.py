from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.simplejson import JSONEncoder
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.db.models.sql.datastructures import EmptyResultSet


class Cell(object):
    def __init__(self, value, cssclass=""):
        self.value = value
        self.cssclass = cssclass

    def as_dict(self):
        return dict(value=self.value, cssclass=self.cssclass)


class RowAction(object):
    def __init__(self, label, url):
        self.label = label
        self.url = url

    def as_dict(self):
        return dict(label=self.label, url=self.url)

class Row(object):
    def __init__(self, id, cssclass="", title=""):
        self.id = id
        self.title = title
        self.cells = []
        self.cssclass = cssclass
        self.actions = []

    def add_cell(self, value, cssclass=""):
        self.cells.append(Cell(unicode(value), cssclass))

    def add_action(self, *args, **kwargs):
        self.actions.append(RowAction(*args, **kwargs))

    def add_actions(self, *rowactions):
        self.actions.extend(rowactions)

    def as_dict(self):
        return dict(
            id = self.id,
            title = self.title,
            cells = [c.as_dict() for c in self.cells],
            cssclass = self.cssclass,
            actions = [a.as_dict() for a in self.actions]
        )

    def __getitem__(self, index):
        return self.cells[index]


class Columns(dict):
    def __init__(self, *cols):
        self.lst = []
        for col in cols:
            self.add(col)

    def get_by_index(self, index):
        """ Get a item by index. """
        return self.lst[index]

    def get_index(self, key):
        """ Return the index of the given ``key``. """
        return self.lst.index(key)

    def iter_ordered(self):
        return self.lst.__iter__()

    def add(self, col):
        if col.id in self:
            raise KeyError("Columns do not support duplicate id's.")
        else:
            self[col.id] = col
            self.lst.append(col)

class Col(object):
    """
    .. attribute:: id

        A unique (within a table) is for this column. This is the value put
        in the ``active_optional_columns`` argument to
        :meth:`FilterTable.create_row`.

    .. attribute:: heading

        The column heading.

    .. attribute:: title

        What users see when hovering over the column header. The title must
        be valid html.

    .. attribute:: can_order

        Can the user order this column? Defaults to False.

    .. attribute:: optional

        Is this column optional (can the user disable it)? Defaults to False.

    .. attribute:: active_default

        If optional is ``True``, this configures if the columns is visible
        by default. Default value is ``False``.
    """
    def __init__(self, id, heading, can_order=False, optional=False,
            active_default=False, title=None):
        """
        All parameters are the same as the class attributes, except for
        ``id`` which is stored as ``str(id)`` to ensure it is a string.
        """
        self.id = str(id)
        self.heading = heading
        self.title = title
        self.can_order = can_order
        self.optional = optional
        self.active_default = active_default

    def as_dict(self):
        return dict(id=self.id, can_order=self.can_order,
                heading=self.heading, title=self.title,
                optional=self.optional, active_default=self.active_default)



class FilterLabel(object):
    """ A label in a filter.
    
    .. attribute:: label

        The label of the filter (the text after the radio/checkbox).

    .. attribute:: title

        The title shown when users hover the label. Defaults to a empty
        string.
    """
    def __init__(self, label, title=""):
        self.label = label
        self.title = title

    def as_dict(self):
        return dict(label=self.label, title=self.title)

FilterLabel.DEFAULT = FilterLabel(_("Don't use this filter"))


class Filter(object):
    """
    .. attribute:: multiselect

        Is the filter multiselect or not? If it is multiselect, the user can
        choose more than one label at one time.
    """
    multiselect = False
    title = None

    def __init__(self, title=None):
        if title:
            self.title = title
        if not self.title:
            raise ValueError("Filters must have a title")

    def get_labels(self, properties):
        """ This is run on each refresh to update the filter view.

        :return: a list of :class:`FilterLabel` objects.
        """
        raise NotImplementedError()

    def filter(self, properties, dataset, selected):
        return dataset

    def as_dict(self, properties, dataset, selected):
        lbls = self.get_labels(properties)
        if not lbls:
            return None
        labels = [{
            'selected': i in selected,
            'labelobj': label.as_dict()}
            for i, label in enumerate(lbls)]
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
    default_perpage = 30
    default_order_by = None
    default_order_asc = True
    use_rowactions = False
    resultcount_supported = False
    search_help = ""
    has_filters = True
    has_related_actions = True
    has_selection_actions = True

    @classmethod
    def initial_html(cls, request, jsonurl):
        return render_to_string('devilry/ui/filtertable.django.html', {
            'id': cls.id,
            'jsonurl': jsonurl,
            'search_help': cls.search_help,
            'has_selection_actions': cls.has_selection_actions,
            'has_related_actions':  cls.has_related_actions,
            'has_search': hasattr(cls, "search"),
            'has_filters': cls.has_filters,
            'resultcount_supported': cls.resultcount_supported
            }, context_instance=RequestContext(request))

    @classmethod
    def get_checkbox_name(cls):
        return '%s-checkbox' % cls.id

    @classmethod
    def get_selected_ids(cls, request):
        return request.POST.getlist(cls.get_checkbox_name())

    def __init__(self, request, **properties):
        self.properties = properties
        self.request = request
        self.indata = request.GET

        def getvar(name):
            if hasattr(self, name):
                return getattr(self, name)
            else:
                return getattr(self, "get_" + name)()
        self.columns = getvar("columns")
        self.filters = getvar("filters")
        self.selectionactions = getvar("selectionactions")
        self.relatedactions = getvar("relatedactions")

        self.session_from_indata()
        #del self.request.session[self.id]


    def get_filters(self):
        return []
    def get_columns(self):
        raise NotImplementedError(
                "columns or get_columns() is required for any FilterTable.")
    def get_selectionactions(self):
        return []
    def get_relatedactions(self):
        return []
        

    def _get_default_filters(self):
        default_filters = {}
        for i, f in enumerate(self.filters):
            default_filters[i] = f.get_default_selected(self.properties)
        return default_filters

    def get_default_session(self):
        default_session = SessionInfo(
            self.default_currentpage, self.default_perpage,
            self.default_order_by, self.default_order_asc,
            self._get_default_filters(),
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
            colid = indata["order_by"]
            if colid in self.columns:
                if colid == self.session.order_by:
                    self.session.order_asc = not self.session.order_asc
                else:
                    self.session.order_asc = True
                    self.session.order_by = colid
        elif self.session.order_by \
                and not self.session.order_by in self.columns:
            self.session.order_asc = self.default_order_asc
            self.session.order_by = self.default_order_by


        checkall_in_filter = int(indata.get("checkall_in_filter", -1))
        default_filters = self._get_default_filters()
        if len(self.session.filters) != len(default_filters):
            self.session.filters = default_filters
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
                

    def create_row(self, item, active_optional_columns):
        """ Called to create a single row in the table.
        
        :param item:
            A single item in the datataset (what the dataset yields
            when iterated).
        :param active_optional_columns:
            A set of active optional columns (columns that the user has
            chosen to see, or that you have set ``active_default``). The
            items in the set are the :attr:`Col.id` of optional columns.
        """
        raise NotImplementedError()

    def create_dataset(self):
        """ Return a iterable dataset, where each item represents one row in
        the table. The only restriction is that it has to be iterable, and
        it has to work with :meth:`create_row`, :meth:`get_dataset_size`,
        :meth:`limit_dataset` and any filters you associate with the table.
        """
        raise NotImplementedError()

    #def search(self, dataset, qry):
        #raise NotImplementedError()

    def get_dataset_size(self, dataset):
        if isinstance(dataset, QuerySet):
            try:
                return dataset.count()
            except EmptyResultSet, e:
                return 0
        else:
            return len(dataset)

    def limit_dataset(self, dataset, start, end):
        return dataset[start:end]

    def get_selectionactions_as_dicts(self):
        return [a.as_dict(self.properties) for a in self.selectionactions]
    def get_relatedactions_as_dicts(self):
        return [a.as_dict(self.properties) for a in self.relatedactions]

    def order_by(self, dataset, colid, order_asc, qryprefix):
        return dataset.order_by(qryprefix + colid)

    def set_properties(self, **properties):
        self.properties.update(properties)

    def create_filterview(self, dataset):
        """ Get a list containing a dictionary for each filter. The
        dictionary is created with :meth:`Filter.as_dict`.

        :param dataset:
            The **unfiltered** dataset returned by :meth:`create_dataset`.
        """
        r = []
        for i, f in enumerate(self.filters):
            dct = f.as_dict(self.properties, dataset, self.session.filters[i])
            if dct:
                r.append(dct)
        return r

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

    def format_active_optional_columns(self, active_optional_columns):
        """ Change/format active optional columns.
        
        The return value from this method is what is sent to
        :meth:`create_row`. By default this only returns
        ``active_optional_columns``.
        
        A typical use case is to do a query on the the id of each optional
        column, and make active_optional_columns be a list of objects
        instead of strings. Since this is only called once (instead of on
        each row) more expensive calculations are possible.
        """
        return active_optional_columns

    def dataset_to_rowlist(self, dataset):
        active_optional_columns = self.format_active_optional_columns(
                self.session.active_optional_columns)
        return [self.create_row(d,
            active_optional_columns).as_dict() for d in dataset]

    def create_jsondata(self):
        totalsize, dataset = self.create_dataset()
        filterview = self.create_filterview(dataset)
        dataset, filteredsize = self.search_and_filter(dataset)
        active_columns = self.get_active_columns()

        order_colnum = -1 # used by js to hilight the sorted column
        if self.session.order_by:
            colids = [c['id'] for c in active_columns]
            #print colids, self.session.order_by
            try:
                order_colnum = colids.index(self.session.order_by)
            except ValueError:
                pass # the order column is not visible.
            else:
                prefix = '-'
                if self.session.order_asc:
                    prefix = ''
                dataset = self.order_by(dataset, self.session.order_by,
                        self.session.order_asc, prefix)

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
            active_columns = active_columns,
            use_rowactions = self.use_rowactions,
            selectionactions = self.get_selectionactions_as_dicts(),
            relatedactions = self.get_relatedactions_as_dicts(),
            order_by = self.session.order_by,
            order_asc = self.session.order_asc,
            order_colnum = order_colnum,
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
