# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import devilry.devilry_comment.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=4096)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('published_datetime', models.DateTimeField(null=True, blank=True)),
                ('user_role', models.CharField(max_length=42, choices=[(b'student', b'Student'), (b'examiner', b'Examiner'), (b'admin', b'Admin')])),
                ('comment_type', models.CharField(max_length=42, choices=[(b'imageannotationcomment', b'ImageAnnotationComment'), (b'groupcomment', b'GroupComment')])),
                ('parent', models.ForeignKey(blank=True, to='devilry_comment.Comment', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CommentFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mimetype', models.CharField(max_length=42)),
                ('file', models.FileField(max_length=512, upload_to=devilry.devilry_comment.models.commentfile_directory_path)),
                ('filename', models.CharField(max_length=255)),
                ('filesize', models.PositiveIntegerField()),
                ('processing_started_datetime', models.DateTimeField(null=True, blank=True)),
                ('processing_completed_datetime', models.DateTimeField(null=True, blank=True)),
                ('processing_successful', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(to='devilry_comment.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='CommentFileImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.FileField(max_length=512, upload_to=devilry.devilry_comment.models.commentfileimage_directory_path)),
                ('image_width', models.PositiveIntegerField()),
                ('image_height', models.PositiveIntegerField()),
                ('thumbnail', models.FileField(max_length=512, upload_to=devilry.devilry_comment.models.commentfileimage_thumbnail_directory_path)),
                ('thumbnail_width', models.PositiveIntegerField()),
                ('thumbnail_height', models.PositiveIntegerField()),
                ('comment_file', models.ForeignKey(to='devilry_comment.CommentFile')),
            ],
        ),
    ]
