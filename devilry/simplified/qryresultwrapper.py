from django.db.models import Q

from utils import modelinstance_to_dict


class QryResultWrapper(object):
    """ Wrapper around a django QuerySet.

    This object can be iterated and indexed::

        print resultdct[0]['myfield']
        for resultdct in qryresultwrapper:
            print resultdct['myfield']

    .. attribute:: resultfields

        The underlying django queryset provides access to far more data
        than what we usually require. This list contains the fields provided
        when methods in this class convert the model instances
        in the wrapped django queryset into a dict.

    .. attribute:: searchfields

        The fields that were searched when generating this result.

    .. attribute:: _insecure_django_qryset

        The django queryset which this object wraps to provide security.
        Should **not** be used unless the public methods of this class
        fails to provide the required functionality. Any use of _insecure_django_qryset
        is considered a security risc.

    .. attribute:: total

        The total number of matches before slicing (before applying start and
        limit).
    """
    def __init__(self, resultfields, searchfields, django_qryset, orderbyfields=[]):
        self.resultfields = resultfields
        self.orderbyfields = set(list(self.resultfields) + orderbyfields)
        self.searchfields = searchfields
        self._insecure_django_qryset = django_qryset
        self._cached_valuesqryset = None

    def __getitem__(self, index):
        """ Get the result at the given ``index`` as a dict. """
        return modelinstance_to_dict(self._insecure_django_qryset[index],
                                     self.resultfields)

    def __len__(self):
        """ Shortcut for ``len(_insecure_django_qryset)``. """
        return len(self._insecure_django_qryset)

    def count(self):
        """ Shortcut for ``_insecure_django_qryset.count()``. """
        return len(self._insecure_django_qryset)
        return self._insecure_django_qryset.count()

    def __iter__(self):
        """ Iterate over all items in the result, yielding a dict
        containing the result data for each item. """
        for item in self._insecure_django_qryset.all():
            yield modelinstance_to_dict(item, self.resultfields)

    def _create_q(self, query):
        """ Create a ``django.db.models.Q`` object from the given
        query. The resulting Q matches data in any field in
        :attr:`resultfields` """
        result_q = None
        for word in query.split():
            if word.strip() == '':
                break
            word_q = self._create_word_q(word)
            if result_q == None:
                result_q = word_q
            else:
                result_q &= word_q
        return result_q

    def _create_word_q(self, queryword):
        filterargs = None
        for field in self.searchfields:
            q = Q(**{"%s__icontains" % field: queryword})
            if filterargs:
                filterargs |= q
            else:
                filterargs = q
        return filterargs


    def _limit_queryset(self, limit, start):
        self._insecure_django_qryset = self._insecure_django_qryset[start:start+limit]

    def _filter_orderby(self, orderby):
        """
        Returns a list of all resultfields in ``orderby`` which is in ``resultfields``
        (including those prefixed with a character, such as '-')
        """
        def filter_test(orderfield):
            return orderfield in self.orderbyfields or \
                    (orderfield[1:] in self.orderbyfields and orderfield[0] == '-')
        return filter(filter_test, orderby)

    def _order_queryset(self, orderby):
        orderby_filtered = self._filter_orderby(orderby)
        self._insecure_django_qryset = self._insecure_django_qryset.order_by(*orderby_filtered)

    def _query_order_and_limit(self, query='', limit=50, start=0, orderby=[]):
        query = query.strip()
        if query:
            q = self._create_q(query)
            self._insecure_django_qryset = self._insecure_django_qryset.filter(q)
        self._insecure_django_qryset = self._insecure_django_qryset.distinct()
        if orderby:
            self._order_queryset(orderby)
        self.total = self._insecure_django_qryset.count()
        self._limit_queryset(limit, start)
