from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('webdemo', '0002_auto_20151207_0351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='publishing_time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The time when this will be visible on the website.', verbose_name='Publishing time'),
            preserve_default=True,
        ),
    ]
