from django.db.models import Q


def _create_q(query, fields):
    qry = None
    for field in fields:
        q = Q(**{"%s__icontains" % field: query})
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

def query_queryset(qryset, query, fields):
    q = _create_q(query, fields)
    if q == None:
        return qryset.all()
    else:
        return qryset.filter(q)

def order_queryset(qryset, orderby, fields):
    orderby_filtered = _filter_orderby(orderby, fields)
    return qryset.order_by(*orderby_filtered)

def limit_queryset(qryset, limit, start):
    return qryset[start:start+limit]


def qry_common(qry, fields, query, queryfields, orderby, limit, start):
    qry = query_queryset(qry, query, queryfields)
    qry = order_queryset(qry, orderby, fields)
    qry = qry.distinct()
    qry = limit_queryset(qry, limit, start)
    return qry
