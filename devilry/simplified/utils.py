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
    return filter(lambda i: i in fields or i[1:] in fields, orderby)

def search_queryset(qryset, search, fields):
    q = _create_q(search, fields)
    if q == None:
        return qryset.all()
    else:
        return qryset.filter(q)

def order_queryset(qryset, orderby, fields):
    return qryset.order_by(*_filter_orderby(orderby, fields))

def limit_queryset(qryset, count, start):
    return qryset[start:start+count]
