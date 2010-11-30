from devilry.core.models import Assignment

import utils


def assignments(user, count=50, start=0, orderby=["short_name"], old=True,
        active=True, search="", longnamefields=False,
        pointhandlingfields=False):
    fields = ["short_name",
            "parentnode__short_name",
            "parentnode__parentnode__short_name"]
    if longnamefields:
        fields.append("long_name")
        fields.append("parentnode__long_name")
        fields.append("parentnode__parentnode__long_name")
    if old and active:
        qry = Assignment.published_where_is_examiner(user)
    else:
        if old:
            qry = Assignment.old_where_is_examiner(user)
        elif active:
            qry = Assignment.active_where_is_examiner(user)
        else:
            qry = Assignment.objects.none()
    qry = utils.search_qryset(qry, search, fields)
    qry = qry.order_by(*utils.filter_orderby(orderby, fields))
    qry = qry.distinct()
    return qry[start:start+count]
