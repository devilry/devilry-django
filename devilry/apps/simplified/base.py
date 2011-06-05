from django.db.models import Q


class GetQryResult(object):
    def __init__(self, fields, queryfields, qryset):
        self.fields = fields
        self.queryfields = queryfields
        self.qryset = qryset

    def valuesQryset(self):
        return self.qryset.values(*self.fields)

    def _create_q(self, query):
        filterargs = None
        for field in self.queryfields:
            q = Q(**{"%s__icontains" % field: query})
            if filterargs:
                filterargs |= q
            else:
                filterargs = q
        return filterargs

    def _query_queryset(self, query):
        q = self._create_q(query)
        if q == None:
            self.qryset = self.qryset.all()
        else:
            self.qryset = self.qryset.filter(q)

    def _distinct(self):
        self.qryset = self.qryset.distinct()

    def _limit_queryset(self, limit, start):
        self.qryset = self.qryset[start:start+limit]

    def _filter_orderby(self, orderby):
        """
        Returns a list of all fields in ``orderby`` which is in ``fields``
        (including those prefixed with a character, such as '-')
        """
        def filter_test(orderfield):
            return orderfield in self.fields or \
                    (orderfield[1:] in self.fields and orderfield[0] == '-')
        return filter(filter_test, orderby)

    def _order_queryset(self, orderby):
        orderby_filtered = self._filter_orderby(orderby)
        self.qryset = self.qryset.order_by(*orderby_filtered)

    def _standard_operations(self, query='', limit=50, start=0, orderby=[]):
        self._query_queryset(query)
        self._distinct()
        if orderby:
            self._order_queryset(orderby)
        self._limit_queryset(limit, start)


class SimplifiedBase(object):

    @classmethod
    def get_default_ordering(cls):
        return cls.CORE_MODEL._meta.ordering

    @classmethod
    def _set_orderby(cls, standard_opts):
        standard_opts['orderby'] = standard_opts.get('orderby',
                cls.get_default_ordering())

    @classmethod
    def get(cls, user, id):
        obj = cls._meta.model.objects.get(id=id)
        cls._authorize(user, obj)
        return obj

    #@classmethod
    #def update(cls, user, **kwargs):
        #obj = cls.get(user, id)
        #for attrname, value in kwargs.iteritems():
            #setattr(obj, attrname, value)
        #cls._set_parentnode_from_id(obj, parentnode_id)
        #obj.full_clean()
        #obj.save()
        #return obj

    #@classmethod
    #def _get(cls, fields, queryfields, qryset, standard_opts):
        #result = GetQryResult(fields, queryfields, qryset)
        #cls._set_orderby(standard_opts)
        #result._standard_operations(**standard_opts)
        #return result

    #@classmethod
    #def _save_model(cls, model):
        #""" Save and validate a model. """
        #model.full_clean()
        #model.save()
