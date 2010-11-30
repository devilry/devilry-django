from django.db.models import Q


def create_q(search, fields):
    qry = None
    for field in fields:
        q = Q(**{"%s__icontains" % field: search})
        if qry:
            qry |= q
        else:
            qry = q
    return qry

def search_qryset(qryset, search, fields):
    q = create_q(search, fields)
    if q == None:
        return qryset.all()
    else:
        return qryset.filter(q)

def filter_orderby(orderby, fields):
    return filter(lambda i: i in fields or i[1:] in fields, orderby)
