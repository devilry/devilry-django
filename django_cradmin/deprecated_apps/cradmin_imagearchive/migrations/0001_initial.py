# -*- coding: utf-8 -*-
from django.db import models, migrations
import django_cradmin.deprecated_apps.cradmin_imagearchive.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveImage',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('role_object_id', models.PositiveIntegerField()),
                ('image', models.ImageField(upload_to=django_cradmin.deprecated_apps.cradmin_imagearchive.models.archiveimage_upload_to, null=True, help_text='Select an image to add to the archive.', verbose_name='image', height_field='image_height', max_length=255, width_field='image_width')),
                ('image_height', models.IntegerField(null=True, blank=True, editable=False)),
                ('image_width', models.IntegerField(null=True, blank=True, editable=False)),
                ('file_extension', models.CharField(max_length=255, editable=False)),
                ('name', models.CharField(max_length=255, blank=True, help_text='Give the image a name (optional). If you leave this blank, the name of the uploaded image file is used.', verbose_name='name')),
                ('description', models.TextField(default='', blank=True, help_text='An optional description of the image. Think if this as a description of the image for visually impaired users. This means that you should describe the information carried in the image (if any).', verbose_name='description')),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('role_content_type', models.ForeignKey(help_text='The role owning this image.', verbose_name='role', to='contenttypes.ContentType', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'archive images',
                'verbose_name': 'archive image',
            },
            bases=(models.Model,),
        ),
    ]
