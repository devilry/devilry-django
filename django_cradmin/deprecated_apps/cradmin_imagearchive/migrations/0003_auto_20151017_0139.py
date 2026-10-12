# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cradmin_imagearchive', '0002_archiveimage_file_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archiveimage',
            name='description',
            field=models.TextField(blank=True, help_text='An optional description of the image. Think if this as a description of the image for visually impaired users. This means that you should describe the information carried in the image (if any). A good description also helps search engines find the image.', verbose_name='description', default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='archiveimage',
            name='name',
            field=models.CharField(blank=True, verbose_name='name', max_length=255),
            preserve_default=True,
        ),
    ]
