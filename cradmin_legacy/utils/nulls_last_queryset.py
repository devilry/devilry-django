from django.db import models, connections


class NullsLastQuery(models.sql.query.Query):
    """
    Query that uses custom compiler,
    to utilize PostgreSQL feature of setting position of NULL records
    """

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]

        # defining that class elsewhere results in import errors
        from django.db.models.sql.compiler import SQLCompiler

        class NullsLastSQLCompiler(SQLCompiler):
            def get_ordering(self):
                result, group_by = super().get_ordering()
                if self.connection.vendor == "postgresql" and result:
                    result = [line + " NULLS LAST" for line in result]
                return result, group_by

        return NullsLastSQLCompiler(self, connection, using)


class NullsLastQuerySet(models.query.QuerySet):
    def __init__(self, model=None, query=None, using=None):
        super().__init__(model, query, using)
        self.query = query or NullsLastQuery(self.model)


class NullsLastManager(models.Manager):
    def get_query_set(self):
        return NullsLastQuerySet(self.model, using=self._db)
