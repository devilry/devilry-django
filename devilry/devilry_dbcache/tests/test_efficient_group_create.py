from __future__ import unicode_literals

from django import test
from django.db.models import AutoField
from django.db.models.sql import InsertQuery
from django.db.models.sql.compiler import SQLInsertCompiler
from model_mommy import mommy
from django.db import connection

from devilry.apps.core.models import AssignmentGroup, Candidate


class TestBulkInsert(test.TestCase):
    def test_stuff(self):
        # BulkInsert(
        #     AssignmentGroup(),
        #     [
        #         [
        #             Candidate(relatedstudent=mommy.make('core.RelatedStudent')),
        #         ],
        #     ]
        # ])
        # group = AssignmentGroup(name='test')
        # non_pks = [f for f in group._meta.local_concrete_fields if not f.primary_key]
        # values = [(field, getattr(group, field.attname))
        #           for field in non_pks]

        # print
        # print"*" * 70
        # print
        # for field, value in values:
        #     print field.name, field.get_db_prep_save(value, connection)
        # print
        # print"*" * 70
        # print

        # print()
        # print("*" * 70)
        # print()
        # print(connection.ops.bulk_insert_sql(non_pks, 1))
        # print()
        # print("*" * 70)
        # print()
        # print()
        # print("*" * 70)
        # print()
        # print(AssignmentGroup._meta.db_table)
        # print()
        # print("*" * 70)
        # print()



        assignment = mommy.make('core.Assignment')
        # sql, values = BulkInsertList([
        #     BulkInsert(
        #         modelobject=AssignmentGroup(name='test', parentnode=assignment),
        #         children=[
        #             ChildInsertList(
        #                 parent_fieldname='assignment_group_id',
        #                 childinserts=[
        #                     ChildInsert(mommy.prepare('core.Candidate'))
        #                 ]
        #             )
        #         ])
        # ]).to_sql()
        # print sql
        # print values

        # print bulk_insert_and_return_ids(AssignmentGroup, [
        #     AssignmentGroup(name='test1', parentnode=assignment),
        #     AssignmentGroup(name='test2', parentnode=assignment),
        # ])
        group_ids = AssignmentGroup.objects.posgres_bulk_create_and_return_ids([
            AssignmentGroup(name='test1', parentnode=assignment),
            AssignmentGroup(name='test2', parentnode=assignment),
            AssignmentGroup(name='test3', parentnode=assignment),
        ], batch_size=2)
        print group_ids
        # for sql, values in groups:
        #     print sql
        #     print values
        #     print
        # print groups[0].id
