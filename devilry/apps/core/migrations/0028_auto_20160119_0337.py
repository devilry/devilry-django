# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20160116_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='students_can_see_points',
            field=models.BooleanField(default=False, verbose_name='Students can see points?'),
        ),
    ]
