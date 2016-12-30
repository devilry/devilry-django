from __future__ import unicode_literals

import itertools

from django.db import connections
from django.db import transaction
from django.db.models import AutoField


class BulkInsertSQLBuilder(object):
    def __init__(self, model_class, objs, connection, fields):
        self.raw = False
        self.model_class = model_class
        self.objs = objs
        self.connection = connection
        self.fields = fields

    def _create_db_prepared_values_from_object(self, obj):
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


class PostgresBulkInsert(object):
    def __init__(self, queryset, model_class, db, objs, batch_size):
        self.queryset = queryset
        self.model_class = model_class
        self.db = db
        self.connection = connections[db]

        self.fields = self.model_class._meta.local_concrete_fields
        self.fields = [field for field in self.fields if not isinstance(field, AutoField)]

        ops = self.connection.ops
        self.batch_size = (batch_size or max(ops.bulk_batch_size(self.fields, objs), 1))

        self.sql_list = self._build_sql(objs=objs)

    def _build_sql(self, objs):
        sql_list = []
        with transaction.atomic(using=self.db, savepoint=False):
            for batch in [objs[i:i + self.batch_size]
                          for i in range(0, len(objs), self.batch_size)]:
                sql, params = BulkInsertSQLBuilder(
                    model_class=self.model_class, objs=batch, connection=self.connection,
                    fields=self.fields).to_sql()
                sql_list.append((sql, params))
        return sql_list

    def execute(self):
        ids = []
        cursor = self.connection.cursor()
        for sql, params in self.sql_list:
            cursor.execute(sql, params)
            resultrows = cursor.fetchall()
            ids.extend(resultrow[0] for resultrow in resultrows)
        cursor.close()
        return ids

    def execute_and_return_objects(self):
        ids = self.execute()
        object_dict = self.queryset.in_bulk(ids)
        return [object_dict[id] for id in ids]

    def _group_params(self, params):
        fieldindex_iterator = itertools.cycle(range(len(self.fields)))
        current_row = None
        rows = []
        for index, param in enumerate(params):
            fieldindex = fieldindex_iterator.next()
            if fieldindex == 0:
                current_row = []
                rows.append(current_row)
            current_row.append(param)
        return rows

    def explain(self, compact=False):
        querystring = ''
        for sql, params in self.sql_list:
            querystring += sql
            if compact:
                querystring += '\n-- VALUES:\n'
                for paramlist in self._group_params(params):
                    querystring += '-- [{}]\n'.format(', '.join([repr(param) for param in paramlist]))
                querystring += '\n\n'
            else:
                querystring += '\n'
                for valuesindex, paramlist in enumerate(self._group_params(params)):
                    querystring += '-- VALUES[{}]:\n'.format(valuesindex)
                    for fieldindex, param in enumerate(paramlist):
                        field = self.fields[fieldindex]
                        querystring += '--   [{}] {}: {!r}\n'.format(fieldindex, field.column, param)
                querystring += '\n\n'
        return querystring


class BulkCreateQuerySetMixin(object):
    def postgres_bulk_create(self, objs, batch_size=None):
        assert batch_size is None or batch_size > 0
        if self.model._meta.parents:
            raise ValueError("Can't bulk create an inherited model")
        if not objs:
            return []
        self._for_write = True
        return PostgresBulkInsert(queryset=self,
                                  model_class=self.model,
                                  db=self.db,
                                  objs=objs,
                                  batch_size=batch_size)
