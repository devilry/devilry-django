from __future__ import unicode_literals

from django.db import connections
from django.db.models import AutoField
from django.db.models.sql import InsertQuery
from django.utils.functional import partition
from django.db import transaction


class BulkInsertSQLBuilder(object):
    def __init__(self, model_class, objs, connection, fields):
        self.raw = False
        self.model_class = model_class
        self.objs = objs
        self.connection = connection
        self.fields = fields

    def _create_db_prepared_values_from_object(self, obj):
        # values = [field.get_db_prep_save(getattr(obj, field.attname), self.connection)
        #           for field in self.fields]
        values = [
            field.get_db_prep_save(
                getattr(obj, field.attname) if self.raw else field.pre_save(obj, True),
                connection=self.connection
            ) for field in self.fields
        ]
        return values

    def _build_values(self):
        all_params = []
        all_value_placeholder_sql = []
        for obj in self.objs:
            values = self._create_db_prepared_values_from_object(obj=obj)
            all_params.extend(values)
            value_placeholder_sql = ', '.join(["%s"] * len(values))
            all_value_placeholder_sql.append('  ({})'.format(value_placeholder_sql))
        return all_params, all_value_placeholder_sql

    def to_sql(self):
        all_params, all_value_placeholder_sql = self._build_values()
        fieldnames = [self.connection.ops.quote_name(field.column) for field in self.fields]
        sql = (
            'INSERT INTO {table_name}\n'
            '  ({fieldnames})\n'
            'VALUES\n'
            '{all_value_placeholder_sql}\n'
            'RETURNING id'
        ).format(
            table_name=self.connection.ops.quote_name(self.model_class._meta.db_table),
            fieldnames=', '.join(fieldnames),
            all_value_placeholder_sql=',\n'.join(all_value_placeholder_sql),
        )
        return sql, all_params


class BulkCreateQuerySetMixin(object):

    def _postgres_bulk_create_and_return_ids_build_sql(self, objs, batch_size, fields, connection):
        sql_list = []
        with transaction.atomic(using=self.db, savepoint=False):
            for batch in [objs[i:i + batch_size]
                          for i in range(0, len(objs), batch_size)]:
                sql, params = BulkInsertSQLBuilder(
                    model_class=self.model, objs=batch, connection=connection,
                    fields=fields).to_sql()
                sql_list.append((sql, params))
        return sql_list

    def _postgres_bulk_create_and_return_ids_execute_sql(self, sql_list, connection):
        ids = []
        for sql, params in sql_list:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            resultrows = cursor.fetchall()
            ids.extend(resultrow[0] for resultrow in resultrows)
        return ids

    def posgres_bulk_create_and_return_ids(self, objs, batch_size=None, debug_sql=False):
        assert batch_size is None or batch_size > 0
        if self.model._meta.parents:
            raise ValueError("Can't bulk create an inherited model")
        if not objs:
            return []
        self._for_write = True

        connection = connections[self.db]
        fields = self.model._meta.local_concrete_fields
        fields = [field for field in fields if not isinstance(field, AutoField)]
        ops = connection.ops
        batch_size = (batch_size or max(ops.bulk_batch_size(fields, objs), 1))

        sql_list = self._postgres_bulk_create_and_return_ids_build_sql(
            objs=objs, batch_size=batch_size, fields=fields, connection=connection)
        if debug_sql:
            return sql_list

        return self._postgres_bulk_create_and_return_ids_execute_sql(
            sql_list=sql_list, connection=connection)
