# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0012_auto_20160107_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackset',
            name='is_last_in_group',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='feedbackset',
            unique_together=set([('group', 'is_last_in_group')]),
        ),
    ]
