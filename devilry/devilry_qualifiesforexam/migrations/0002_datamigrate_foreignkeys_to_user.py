# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from devilry.utils import migrationutils


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_qualifiesforexam', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(migrationutils.create_foreignkey_table_change_sql(
            table='devilry_qualifiesforexam_status',
            field='user',
            old_constraint_name='devilry_qualifiesforex_user_id_522959bf05072244_fk_auth_user_id',
            new_referenced_table='devilry_account_user'
        ))
    ]
