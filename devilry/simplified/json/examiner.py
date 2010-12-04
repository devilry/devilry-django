from django.http import HttpResponse, HttpResponseNotAllowed, \
    HttpResponseBadRequest

from devilry.simplified.examiner import ListAssignments



def list_assignments(request):
    if request.method == "GET":
        form = ListAssignments.GetForm(request.GET)
        if form.is_valid():
            return HttpResponse("Valid")
        else:
            return HttpResponseBadRequest("Bad request")
    else:
        HttpResponseNotAllowed(["GET"])
