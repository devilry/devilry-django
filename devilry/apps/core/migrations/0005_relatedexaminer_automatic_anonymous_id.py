# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_examiner_relatedexaminer'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatedexaminer',
            name='automatic_anonymous_id',
            field=models.CharField(default='', max_length=255, editable=False, blank=True),
        ),
    ]
