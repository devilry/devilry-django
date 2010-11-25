from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.simplejson import JSONEncoder

from devilry.core.models import AssignmentGroup


@login_required
def main(request):
    return render_to_response(
        'devilry/guiexamples/main.html', {
        }, context_instance=RequestContext(request))

@login_required
def help(request):
    return render_to_response(
        'devilry/guiexamples/help.html', {
        }, context_instance=RequestContext(request))


class QryWrapper(object):
    mapping = {}
    def __init__(self, inp, qry):
        self.start = inp.get('start', 0)
        self.count = inp.get('count', 10)
        self.numRows = qry.count()
        self.qry = qry[self.start:self.start+self.count]

    def _convert(self, item):
        dct = {}
        for key, label in self.mapping.iteritems():
            dct[label] = item[key]
        return dct

    def json_encode(self):
        items = [self._convert(x) for x in self.qry.values(
                *self.mapping.keys())]
        result = dict(
                numRows = self.numRows,
                items = items)
        json = JSONEncoder(ensure_ascii=False, indent=2).encode(result)
        return json


class AssignmentGroupQryMapper(QryWrapper):
    mapping = {
        "candidates__student__username": "username",
        "status": "status",
    }


@login_required
def assignmentgroups_qry(request):
    qry = AssignmentGroup.where_is_admin_or_superadmin(request.user)
    json = AssignmentGroupQryMapper(request.GET, qry).json_encode()
    return HttpResponse(json, content_type="application/json")
