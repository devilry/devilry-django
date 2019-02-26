# -*- coding: utf-8 -*-


from django.db import models, migrations
from devilry.utils import migrationutils


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_qualifiesforexam', '0001_initial'),
        ('devilry_account', '0002_datamigrate_auth_user_to_devilry_account_user'),
    ]

    operations = [
        migrations.RunSQL(migrationutils.create_foreignkey_table_change_sql(
            table='devilry_qualifiesforexam_status',
            field='user',
            old_constraint_name='devilry_qualifiesforex_user_id_522959bf05072244_fk_auth_user_id',
            new_referenced_table='devilry_account_user'
        ))
    ]
