# -*- coding: utf-8 -*-


from django.db import models, migrations
import devilry.apps.core.models.custom_db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150915_1127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['short_name'], 'verbose_name': 'assignment', 'verbose_name_plural': 'assignments'},
        ),
        migrations.AlterModelOptions(
            name='period',
            options={'ordering': ['short_name'], 'verbose_name': 'semester', 'verbose_name_plural': 'semesters'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['short_name'], 'verbose_name': 'course', 'verbose_name_plural': 'courses'},
        ),
        migrations.AlterField(
            model_name='assignment',
            name='short_name',
            field=devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', max_length=20, verbose_name='Short name'),
        ),
        migrations.AlterField(
            model_name='node',
            name='short_name',
            field=devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', max_length=20, verbose_name='Short name'),
        ),
        migrations.AlterField(
            model_name='period',
            name='short_name',
            field=devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', max_length=20, verbose_name='Short name'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='short_name',
            field=devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). Used when the name takes too much space.', unique=True, max_length=20, verbose_name='Short name'),
        ),
    ]
