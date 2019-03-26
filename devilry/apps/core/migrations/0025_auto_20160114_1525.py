# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160114_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examiner',
            name='old_reference_not_in_use_user',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
    ]
