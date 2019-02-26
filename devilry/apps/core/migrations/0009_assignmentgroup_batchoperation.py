# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ievv_batchframework', '0001_initial'),
        ('core', '0008_auto_20151222_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentgroup',
            name='batchoperation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ievv_batchframework.BatchOperation', null=True),
        ),
    ]
