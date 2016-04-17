from __future__ import unicode_literals

from django.db import connection
from django.db.models import AutoField
from django.db.models.sql import InsertQuery


def _extract_fieldnames_and_values_from_modelobject(modelobject, exclude_field=None):
    meta = modelobject._meta
    pk_value = modelobject._get_pk_val(meta)
    if pk_value is None:
        pk_value = meta.pk.get_pk_value_on_save(modelobject)
    pk_is_set = pk_value is not None
    fields = meta.local_concrete_fields
    if not pk_is_set:
        fields = [field for field in fields if not isinstance(field, AutoField)]

    if exclude_field:
        try:
            fields.remove(exclude_field)
        except ValueError:
            pass

    values = [field.get_db_prep_save(getattr(modelobject, field.attname), connection)
              for field in fields]
    fieldnames = [connection.ops.quote_name(field.name) for field in fields]
    return fieldnames, values


class ChildInsert(object):
    def __init__(self, modelobject):
        self.modelobject = modelobject

    def to_sql(self, parent_fieldname):
        fieldnames, values = _extract_fieldnames_and_values_from_modelobject(
            self.modelobject, exclude_field=parent_fieldname)
        fieldnames.append(connection.ops.quote_name(parent_fieldname))
        value_placeholders = ', '.join(["%s"] * len(values))
        # sql = (
        #     ' INSERT INTO {table_name}\n'
        #     '  ({fieldnames})\n'
        #     ' SELECT {value_placeholders} inserted_object.id'.format(
        #     table_name=connection.ops.quote_name(self.modelobject._meta.db_table),
        #     fieldnames=', '.join(fieldnames),
        #     value_placeholders=value_placeholders
        # )
        sql = ''
        return sql, values


class ChildInsertList(object):
    def __init__(self, parent_fieldname, childinserts):
        self.parent_fieldname = parent_fieldname
        self.childinserts = childinserts

    def to_sql(self):
        full_sql = ''
        all_values = []
        for childinsert in self.childinserts:
            sql, values = childinsert.to_sql(parent_fieldname=self.parent_fieldname)
            full_sql += sql
            all_values.extend(values)
        return full_sql, all_values


class BulkInsert(object):
    def __init__(self, modelobject, children=None):
        self.modelobject = modelobject
        self.children = children

    def to_sql(self):
        fieldnames, values = _extract_fieldnames_and_values_from_modelobject(self.modelobject)
        sql = (
            'WITH inserted_object AS (\n'
            '  INSERT INTO {table_name} ({fieldnames})\n'
            '  {values}\n'
            '  RETURNING id\n'
            ')'
        ).format(
            table_name=connection.ops.quote_name(self.modelobject._meta.db_table),
            fieldnames=', '.join(fieldnames),
            values=connection.ops.bulk_insert_sql(values, 1))
        if self.children:
            for child in self.children:
                child_sql, child_values = child.to_sql()
                sql += child_sql
                child_values.extend(child_values)
        else:
            sql += ';'
        return sql, values


class BulkInsertList(object):
    def __init__(self, bulk_inserts):
        self.bulk_inserts = bulk_inserts

    def to_sql(self):
        full_sql = ''
        all_values = []
        for bulk_insert in self.bulk_inserts:
            sql, values = bulk_insert.to_sql()
            full_sql += sql
            all_values.extend(values)
        return full_sql, all_values


# class EfficientBulkInsert(object):
#     def __init__(self, items):
#         self.insert_statements = []
#         self._build_query(items=items)
#
#     def _make_insert_statement_from_model(self, model):
#         pass
#
#     def _build_query(self, items):
#         for model, childgroups in items:
#             self.insert_statements.append(self._make_insert_statement_from_model(model=model))
#             if childgroups:
#                 self._build_query(childgroups)
#
#     def to_sql(self):
#         return '\n'.join(self.insert_statements)
