# -*- coding: utf-8 -*-


from django.db import models, migrations
import devilry.devilry_comment.models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0002_auto_20160109_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentfileimage',
            name='image',
            field=models.FileField(default='', max_length=512, upload_to=devilry.devilry_comment.models.commentfileimage_directory_path, blank=True),
        ),
        migrations.AlterField(
            model_name='commentfileimage',
            name='thumbnail',
            field=models.FileField(default='', max_length=512, upload_to=devilry.devilry_comment.models.commentfileimage_thumbnail_directory_path, blank=True),
        ),
    ]
