# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeadlineTag'
        db.create_table('devilry_qualifiesforexam_deadlinetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('devilry_qualifiesforexam', ['DeadlineTag'])

        # Adding model 'PeriodTag'
        db.create_table('devilry_qualifiesforexam_periodtag', (
            ('period', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Period'], unique=True, primary_key=True)),
            ('deadlinetag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devilry_qualifiesforexam.DeadlineTag'])),
        ))
        db.send_create_signal('devilry_qualifiesforexam', ['PeriodTag'])

        # Adding model 'Status'
        db.create_table('devilry_qualifiesforexam_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(related_name='qualifiedforexams_status', to=orm['core.Period'])),
            ('status', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('createtime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('plugin', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('exported_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('devilry_qualifiesforexam', ['Status'])

        # Adding model 'QualifiesForFinalExam'
        db.create_table('devilry_qualifiesforexam_qualifiesforfinalexam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('relatedstudent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.RelatedStudent'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(related_name='students', to=orm['devilry_qualifiesforexam.Status'])),
            ('qualifies', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('devilry_qualifiesforexam', ['QualifiesForFinalExam'])

        # Adding unique constraint on 'QualifiesForFinalExam', fields ['relatedstudent', 'status']
        db.create_unique('devilry_qualifiesforexam_qualifiesforfinalexam', ['relatedstudent_id', 'status_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'QualifiesForFinalExam', fields ['relatedstudent', 'status']
        db.delete_unique('devilry_qualifiesforexam_qualifiesforfinalexam', ['relatedstudent_id', 'status_id'])

        # Deleting model 'DeadlineTag'
        db.delete_table('devilry_qualifiesforexam_deadlinetag')

        # Deleting model 'PeriodTag'
        db.delete_table('devilry_qualifiesforexam_periodtag')

        # Deleting model 'Status'
        db.delete_table('devilry_qualifiesforexam_status')

        # Deleting model 'QualifiesForFinalExam'
        db.delete_table('devilry_qualifiesforexam_qualifiesforfinalexam')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.node': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Node'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_nodes'", 'null': 'True', 'to': "orm['core.Node']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'})
        },
        'core.period': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Period'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periods'", 'to': "orm['core.Subject']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.relatedstudent': {
            'Meta': {'unique_together': "(('period', 'user'),)", 'object_name': 'RelatedStudent'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Period']"}),
            'tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.subject': {
            'Meta': {'ordering': "['short_name']", 'object_name': 'Subject'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': "orm['core.Node']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'unique': 'True', 'max_length': '20'})
        },
        'devilry_qualifiesforexam.deadlinetag': {
            'Meta': {'object_name': 'DeadlineTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'devilry_qualifiesforexam.periodtag': {
            'Meta': {'object_name': 'PeriodTag'},
            'deadlinetag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devilry_qualifiesforexam.DeadlineTag']"}),
            'period': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Period']", 'unique': 'True', 'primary_key': 'True'})
        },
        'devilry_qualifiesforexam.qualifiesforfinalexam': {
            'Meta': {'unique_together': "(('relatedstudent', 'status'),)", 'object_name': 'QualifiesForFinalExam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qualifies': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'relatedstudent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.RelatedStudent']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'students'", 'to': "orm['devilry_qualifiesforexam.Status']"})
        },
        'devilry_qualifiesforexam.status': {
            'Meta': {'ordering': "['-createtime']", 'object_name': 'Status'},
            'createtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exported_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'qualifiedforexams_status'", 'to': "orm['core.Period']"}),
            'plugin': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['devilry_qualifiesforexam']