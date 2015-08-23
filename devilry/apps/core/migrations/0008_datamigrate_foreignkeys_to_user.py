# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


operations = []
for spec in [
        {
            'table': 'core_node_admins',
            'old_constraint': 'core_node_admins_user_id_168b63ac6db71014_fk_auth_user_id',
        },
        {
            'table': 'core_subject_admins',
            'old_constraint': 'core_subject_admins_user_id_757b64082c3dd225_fk_auth_user_id',
        },
        {
            'table': 'core_period_admins',
            'old_constraint': 'core_period_admins_user_id_eb067c4bde098ff_fk_auth_user_id',
        },
        {
            'table': 'core_assignment_admins',
            'old_constraint': 'core_assignment_admins_user_id_51116d5a7e12d3b_fk_auth_user_id',
        },
        {
            'table': 'core_candidate',
            'old_constraint': 'core_candidate_student_id_3cfef9dad22e18db_fk_auth_user_id',
            'field': 'student',
        },
        {
            'table': 'core_assignmentgroup_examiners',
            'old_constraint': 'core_assignmentgroup_e_user_id_1a363f9e86525194_fk_auth_user_id',
        },
        {
            'table': 'core_deadline',
            'field': 'added_by',
            'old_constraint': 'core_deadline_added_by_id_5715a513f2acd9ff_fk_auth_user_id',
        },
        {
            'table': 'core_groupinvite',
            'field': 'sent_by',
            'old_constraint': 'core_groupinvite_sent_by_id_1efa01196ad2f009_fk_auth_user_id',
        },
        {
            'table': 'core_groupinvite',
            'field': 'sent_to',
            'old_constraint': 'core_groupinvite_sent_to_id_50bd8691e6283e67_fk_auth_user_id',
        },
        {
            'table': 'core_relatedstudent',
            'old_constraint': 'core_relatedstudent_user_id_66588181cfc595a_fk_auth_user_id',
        },
        {
            'table': 'core_relatedexaminer',
            'old_constraint': 'core_relatedexaminer_user_id_644ee92d6b54d587_fk_auth_user_id',
        },
        {
            'table': 'core_staticfeedback',
            'field': 'saved_by',
            'old_constraint': 'core_staticfeedbac_saved_by_id_5c9526c62cf55415_fk_auth_user_id',
        },
]:
    if 'field' not in spec:
        spec['field'] = 'user'
    spec['new_constraint'] = '{table}_{field}_id_fk_devilry_account_user_id'.format(
        table=spec['table'],
        field=spec['field']
    )
    operations.append(
        migrations.RunSQL("""
            ALTER TABLE {table}
              DROP CONSTRAINT {old_constraint};
            ALTER TABLE {table}
              ADD CONSTRAINT {new_constraint}
              FOREIGN KEY ({field}_id)
              REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;
        """.format(**spec))
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150601_2125'),
        ('devilry_account', '0002_datamigrate_auth_user_to_devilry_account_user'),
    ]

    operations = operations
