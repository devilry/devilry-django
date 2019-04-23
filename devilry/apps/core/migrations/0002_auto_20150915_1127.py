# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='relatedstudent',
            field=models.ForeignKey(default=None, blank=True, to='core.RelatedStudent', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='relatedstudent',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
