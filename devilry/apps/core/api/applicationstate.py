from django.db import connection
from django.http import HttpResponse
from django.views import View


class ReadyCheck(View):
    """
    Is the application ready to accept connections?
    
    Checks if it's possible to fetch from the database. This endpoint 
    should only be called until it returns 200.

    NOTE: If it's needed to continously check if the application is alive, 
    use the "devilry_core/_api/application-state/alive" endpoint.

    Returns 200 OK response if ready, otherwise 503 is returned.
    """
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            one = cursor.fetchone()[0]
            if one != 1:
                return HttpResponse(status=503)
        return HttpResponse()


class LiveCheck(View):
    """
    Check if application is "alive".

    Returns 200 response.
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse()
