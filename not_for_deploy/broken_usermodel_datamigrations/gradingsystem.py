# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from devilry.utils import migrationutils


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_gradingsystem', '0001_initial'),
        ('devilry_account', '0002_datamigrate_auth_user_to_devilry_account_user'),
    ]

    operations = [
        migrations.RunSQL(migrationutils.create_foreignkey_table_change_sql(
            table='devilry_gradingsystem_feedbackdraft',
            field='saved_by',
            old_constraint_name='devilry_gradingsys_saved_by_id_2688417740fdf346_fk_auth_user_id',
            new_referenced_table='devilry_account_user'
        ))
    ]
