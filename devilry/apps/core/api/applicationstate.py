import logging

from django.db import connection
from django.http import HttpResponse
from django.views import View

from django.conf import settings

logger = logging.getLogger(__name__)

class HealthCheckError(Exception):
    """
    Raised when healthchecks fail.
    """



class ReadyCheck(View):
    """
    Is the application ready to accept connections?
    
    Checks if it's possible to fetch from the database. This endpoint 
    should only be called until it returns 200.

    NOTE: If it's needed to continously check if the application is alive, 
    use the "devilry_core/_api/application-state/alive" endpoint.

    Returns 200 OK response if ready, otherwise 503 is returned.
    """

    def healthcheck_django_rq_connections(self):
        """
        Health check all django-rq connections (all configured RQ_QUEUES).

        Raises `HealthCheckError` if the checks fail.
        """
        if not hasattr(settings, 'RQ_QUEUES'):
            return
        for config_name, config in settings.RQ_QUEUES.items():
            try:
                from redis.client import Redis
                connection = Redis(
                    host=config.get('HOST'),
                    db=config.get('DB', 0),
                    port=config.get('PORT'),
                    ssl=config.get('SSL'),
                    ssl_cert_reqs=config.get('SSL_CERT_REQS', None),
                    password=config.get('PASSWORD', None)
                )
                connection.ping()
            except Exception as e:
                logger.exception(e)
                raise HealthCheckError(f"django-rq: cannot connect to queue {config_name!r}.")

    def healthcheck_database_connections(self):
        """
        Health check all database connections (all configured DATABASES).

        Raises `HealthCheckError` if the checks fail.
        """
        db_response_error = False
        try:
            from django.db import connections
            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    db_response_error = True
        except Exception as e:
            logger.exception(e)
            raise HealthCheckError("db: cannot connect to database.")
        if db_response_error:
            raise HealthCheckError("db: invalid response")

    def get(self, request, *args, **kwargs):
        try:
            self.healthcheck_django_rq_connections()
            self.healthcheck_database_connections()
        except HealthCheckError as e:
            logger.exception(e)
            return HttpResponse(status=503)
        return HttpResponse()


class LiveCheck(View):
    """
    Check if application is "alive".

    Returns 200 response.
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse()
