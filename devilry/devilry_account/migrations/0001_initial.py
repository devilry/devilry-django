# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('shortname', models.CharField(help_text='The short name for the user. This is set automatically to the email or username depending on the method used for authentication.', unique=True, max_length=255)),
                ('fullname', models.TextField(default='', verbose_name='Full name', blank=True)),
                ('lastname', models.TextField(default='', verbose_name='Last name', blank=True)),
                ('datetime_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('suspended_datetime', models.DateTimeField(help_text='Time when the account was suspended', null=True, verbose_name='Suspension time', blank=True)),
                ('suspended_reason', models.TextField(default='', verbose_name='Reason for suspension', blank=True)),
                ('languagecode', models.CharField(default='', max_length=10, verbose_name='Preferred language', blank=True)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='UserEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('last_updated_datetime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='Email')),
                ('use_for_notifications', models.BooleanField(default=True, verbose_name='Send notifications to this email address?')),
                ('is_primary', models.NullBooleanField(help_text='Your primary email is the email address used when we need to display a single email address.', verbose_name='Is this your primary email?', choices=[(None, 'No'), (True, 'Yes')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Email address',
                'verbose_name_plural': 'Email addresses',
            },
        ),
        migrations.CreateModel(
            name='UserName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('last_updated_datetime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('username', models.CharField(unique=True, max_length=255, verbose_name='Username')),
                ('is_primary', models.NullBooleanField(help_text='Your primary username is shown alongside your full name to identify you to teachers, examiners and other students.', verbose_name='Is this your primary username?', choices=[(None, 'No'), (True, 'Yes')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Username',
                'verbose_name_plural': 'Usernames',
            },
        ),
        migrations.AlterUniqueTogether(
            name='username',
            unique_together=set([('user', 'is_primary')]),
        ),
        migrations.AlterUniqueTogether(
            name='useremail',
            unique_together=set([('user', 'is_primary')]),
        ),
    ]
