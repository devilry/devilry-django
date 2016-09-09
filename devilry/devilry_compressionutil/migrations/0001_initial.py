# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-09 17:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompressedArchiveMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object_id', models.PositiveIntegerField()),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('archive_name', models.CharField(max_length=200)),
                ('archive_path', models.CharField(max_length=200)),
                ('archive_size', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_compressed_file_meta', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='compressedarchivemeta',
            unique_together=set([('content_type', 'content_object_id')]),
        ),
    ]
