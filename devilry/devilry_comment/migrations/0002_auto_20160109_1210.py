# -*- coding: utf-8 -*-


from django.db import models, migrations
import devilry.devilry_comment.models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='draft_text',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AlterField(
            model_name='commentfile',
            name='file',
            field=models.FileField(default='', max_length=512, upload_to=devilry.devilry_comment.models.commentfile_directory_path, blank=True),
        ),
    ]
