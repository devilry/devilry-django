# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import devilry.devilry_student.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedDeliveryFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uploaded_datetime', models.DateTimeField(auto_now_add=True)),
                ('uploaded_file', models.FileField(upload_to=devilry.devilry_student.models.uploaded_deliveryfile_path)),
                ('filename', models.CharField(max_length=255)),
                ('deadline', models.ForeignKey(to='core.Deadline')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='uploadeddeliveryfile',
            unique_together=set([('deadline', 'user', 'filename')]),
        ),
    ]
