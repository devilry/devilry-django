# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackset',
            name='gradeform_json',
            field=models.TextField(null=True, blank=True),
        ),
    ]
