# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0016_auto_20160114_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackset',
            name='feedbackset_type',
            field=models.CharField(default='first_attempt', max_length=50, db_index=True, choices=[('first_attempt', 'first attempt'), ('new_attempt', 'new attempt'), ('re_edit', 're edit')]),
        ),
    ]
