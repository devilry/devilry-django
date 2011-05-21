from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.simplejson import JSONEncoder
from django.db.models import Avg
from django.core import serializers

from devilry.core.models import AssignmentGroup, Assignment


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
        self.start = int(inp.get('start', 0))
        self.count = int(inp.get('count', 10))
        self.numRows = qry.count()
        self.qry = qry[self.start:self.start+self.count]

    def json_encode(self):
        items = [x for x in self.qry]
        #result = dict(
                #numRows = self.numRows,
                #items = items)
        json = JSONEncoder(ensure_ascii=False, indent=2).encode(items)
        return json



@login_required
def assignmentgroups_qry(request):
    qry = AssignmentGroup.where_is_admin_or_superadmin(request.user)
    qry = qry.values("candidates__student__username", "status",
            "scaled_points")
    print request.GET
    json = QryWrapper(request.GET, qry).json_encode()
    return HttpResponse(json, content_type="application/json")


@login_required
def assignment_avg_labels(request):
    qry = Assignment.where_is_admin_or_superadmin(request.user).order_by("publishing_time")
    labels = [dict(value=i+1, text=x[0]) \
            for i, x in enumerate(qry.values_list("short_name"))]
    json = JSONEncoder(ensure_ascii=False, indent=2).encode(labels)
    return HttpResponse(json, content_type="application/json")

@login_required
def assignment_avg_data(request):
    qry = Assignment.where_is_admin_or_superadmin(request.user).order_by("publishing_time")
    qry = qry.annotate(
            avg_scaled_points = Avg("assignmentgroups__scaled_points"))
    qry = qry.values("avg_scaled_points")
    json = QryWrapper(request.GET, qry).json_encode()
    return HttpResponse(json, content_type="application/json")

@login_required
def all_users(request):
    #page = int(request.GET['page'])
    #limit = int(request.GET['limit'])
    qry = User.objects.all()
    items = qry.values('username', 'email')
    json = JSONEncoder(ensure_ascii=False, indent=2).encode(
            {'success':True, 'users': [x for x in items]})
    return HttpResponse(json, content_type="application/json")

@login_required
def update_users(request):
    print request.GET
    json = JSONEncoder().encode({'success':True})
    return HttpResponse(json, content_type="application/json")
