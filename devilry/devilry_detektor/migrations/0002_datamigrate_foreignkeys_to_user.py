# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from devilry.utils import migrationutils


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_detektor', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(migrationutils.create_foreignkey_table_change_sql(
            table='devilry_detektor_detektorassignment',
            field='processing_started_by',
            old_constraint_name='devil_processing_started_by_id_6e7a3417de9d819d_fk_auth_user_id',
            new_referenced_table='devilry_account_user'
        ))
    ]
