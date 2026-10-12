# -*- coding: utf-8 -*-
from django.db import models, migrations
import django_cradmin.deprecated_apps.cradmin_temporaryfileuploadstore.models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporaryFile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('filename', models.TextField(db_index=True)),
                ('file', models.FileField(upload_to=django_cradmin.deprecated_apps.cradmin_temporaryfileuploadstore.models.temporary_file_upload_to)),
                ('mimetype', models.TextField(blank=True, default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryFileCollection',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('minutes_to_live', models.PositiveIntegerField(default=60, help_text='The number of minutes the app requests that this file collection should be kept before automatic removal. This is used by automatic cleanup jobs to determine what to delete. You should not rely on the file beeing automatically deleted after this number of minutes, and you should always delete files explicitly as part of the file upload process.')),
                ('accept', models.TextField(blank=True, default='', help_text='An html input field accept attribute formatted string. This is validated by the API on upload.')),
                ('max_filename_length', models.IntegerField(blank=True, default=None, null=True, help_text='If specified, we shorten filenames to maximum the specified length. This is validated by the API on upload.')),
                ('unique_filenames', models.BooleanField(default=False, help_text='If this is True, we add random data when we detect duplicate filenames. The duplicate prevention algorithm handles max_filename.This is validated by the API on upload.')),
                ('user', models.ForeignKey(help_text='The user that owns this temporary file. Users should notbe allowed access to other users temporary files.', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='temporaryfile',
            name='collection',
            field=models.ForeignKey(related_name='files', to='cradmin_temporaryfileuploadstore.TemporaryFileCollection', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
