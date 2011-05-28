from django.db.models import Q


def _create_q(search, fields):
    qry = None
    for field in fields:
        q = Q(**{"%s__icontains" % field: search})
        if qry:
            qry |= q
        else:
            qry = q
    return qry

def _filter_orderby(orderby, fields):
    """
    Returns a list of all fields in ``orderby`` which is in ``fields``
    (including those prefixed with a character, such as '-')
    """
    def filter_test(orderfield):
        return orderfield in fields or \
                (orderfield[1:] in fields and orderfield[0] == '-')
    return filter(filter_test, orderby)

def search_queryset(qryset, search, fields):
    q = _create_q(search, fields)
    if q == None:
        return qryset.all()
    else:
        return qryset.filter(q)

def order_queryset(qryset, orderby, fields):
    orderby_filtered = _filter_orderby(orderby, fields)
    return qryset.order_by(*orderby_filtered)

def limit_queryset(qryset, count, start):
    return qryset[start:start+count]


def qry_common(qry, fields, search, searchfields, orderby, count, start):
    qry = search_queryset(qry, search, searchfields)
    qry = order_queryset(qry, orderby, fields)
    qry = qry.distinct()
    qry = limit_queryset(qry, count, start)
    return qry
