from django.db import models, connections
from django.db.models import sql


class NullsLastQuery(sql.Query):
    def get_compiler(self, using=None, connection=None, *args, **kwargs):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]

        # defining that class elsewhere results in import errors
        from django.db.models.sql.compiler import SQLCompiler

        class NullsLastSQLCompiler(SQLCompiler):
            def get_order_by(self):
                results = super(NullsLastSQLCompiler, self).get_order_by()

                if self.connection.vendor == "postgresql" and results:
                    results = [(result[0], (result[1][0] + " NULLS LAST",) + result[1][1:]) for result in results]

                return results

        return NullsLastSQLCompiler(self, connection, using)


class NullsLastQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(NullsLastQuerySet, self).__init__(model, query, using, hints)
        self.query = query or NullsLastQuery(self.model)
