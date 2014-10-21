# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DetectorAssignment'
        db.create_table('devilry_detektor_detectorassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assignment', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Assignment'], unique=True)),
            ('processing_started_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('processing_ended_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('processing_started_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('devilry_detektor', ['DetectorAssignment'])


    def backwards(self, orm):
        # Deleting model 'DetectorAssignment'
        db.delete_table('devilry_detektor_detectorassignment')


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
        'core.assignment': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Assignment'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadline_handling': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'delivery_types': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'examiners_publish_feedbacks_directly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'first_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'grading_system_plugin_id': ('django.db.models.fields.CharField', [], {'default': "'devilry_gradingsystemplugin_approved'", 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'max_points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['core.Period']"}),
            'passing_grade_min_points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'points_to_grade_mapper': ('django.db.models.fields.CharField', [], {'default': "'passed-failed'", 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'publishing_time': ('django.db.models.fields.DateTimeField', [], {}),
            'scale_points_percent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'}),
            'students_can_create_groups': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'students_can_not_create_groups_after': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'students_can_see_points': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
        'core.subject': {
            'Meta': {'ordering': "['short_name']", 'object_name': 'Subject'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': "orm['core.Node']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'unique': 'True', 'max_length': '20'})
        },
        'devilry_detektor.detectorassignment': {
            'Meta': {'object_name': 'DetectorAssignment'},
            'assignment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Assignment']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_ended_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'processing_started_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'processing_started_datetime': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['devilry_detektor']