# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DetektorAssignment'
        db.create_table('devilry_detektor_detektorassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assignment', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Assignment'], unique=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='unprocessed', max_length=12)),
            ('processing_started_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('processing_started_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('devilry_detektor', ['DetektorAssignment'])

        # Adding model 'DetektorDeliveryParseResult'
        db.create_table('devilry_detektor_detektordeliveryparseresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('detektorassignment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parseresults', to=orm['devilry_detektor.DetektorAssignment'])),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Delivery'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('operators_string', self.gf('django.db.models.fields.TextField')()),
            ('keywords_string', self.gf('django.db.models.fields.TextField')()),
            ('number_of_operators', self.gf('django.db.models.fields.IntegerField')()),
            ('number_of_keywords', self.gf('django.db.models.fields.IntegerField')()),
            ('operators_and_keywords_string', self.gf('django.db.models.fields.TextField')()),
            ('normalized_sourcecode', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parsed_functions_json', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('devilry_detektor', ['DetektorDeliveryParseResult'])

        # Adding unique constraint on 'DetektorDeliveryParseResult', fields ['delivery', 'language']
        db.create_unique('devilry_detektor_detektordeliveryparseresult', ['delivery_id', 'language'])

        # Adding model 'DetektorAssignmentCacheLanguage'
        db.create_table('devilry_detektor_detektorassignmentcachelanguage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('detektorassignment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cachelanguages', to=orm['devilry_detektor.DetektorAssignment'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('devilry_detektor', ['DetektorAssignmentCacheLanguage'])

        # Adding unique constraint on 'DetektorAssignmentCacheLanguage', fields ['detektorassignment', 'language']
        db.create_unique('devilry_detektor_detektorassignmentcachelanguage', ['detektorassignment_id', 'language'])

        # Adding model 'CompareTwoCacheItem'
        db.create_table('devilry_detektor_comparetwocacheitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comparetwo_cacheitems', to=orm['devilry_detektor.DetektorAssignmentCacheLanguage'])),
            ('parseresult1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['devilry_detektor.DetektorDeliveryParseResult'])),
            ('parseresult2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['devilry_detektor.DetektorDeliveryParseResult'])),
            ('scaled_points', self.gf('django.db.models.fields.IntegerField')()),
            ('summary_json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('devilry_detektor', ['CompareTwoCacheItem'])


    def backwards(self, orm):
        # Removing unique constraint on 'DetektorAssignmentCacheLanguage', fields ['detektorassignment', 'language']
        db.delete_unique('devilry_detektor_detektorassignmentcachelanguage', ['detektorassignment_id', 'language'])

        # Removing unique constraint on 'DetektorDeliveryParseResult', fields ['delivery', 'language']
        db.delete_unique('devilry_detektor_detektordeliveryparseresult', ['delivery_id', 'language'])

        # Deleting model 'DetektorAssignment'
        db.delete_table('devilry_detektor_detektorassignment')

        # Deleting model 'DetektorDeliveryParseResult'
        db.delete_table('devilry_detektor_detektordeliveryparseresult')

        # Deleting model 'DetektorAssignmentCacheLanguage'
        db.delete_table('devilry_detektor_detektorassignmentcachelanguage')

        # Deleting model 'CompareTwoCacheItem'
        db.delete_table('devilry_detektor_comparetwocacheitem')


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
        'core.assignmentgroup': {
            'Meta': {'ordering': "['id']", 'object_name': 'AssignmentGroup'},
            'delivery_status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.StaticFeedback']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_deadline': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_deadline_for_group'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Deadline']", 'blank': 'True', 'unique': 'True'}),
            'last_delivery': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_delivery_by_group'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Delivery']", 'blank': 'True', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignmentgroups'", 'to': "orm['core.Assignment']"})
        },
        'core.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'candidates'", 'to': "orm['core.AssignmentGroup']"}),
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.deadline': {
            'Meta': {'ordering': "['-deadline']", 'object_name': 'Deadline'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deadlines'", 'to': "orm['core.AssignmentGroup']"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'deliveries_available_before_deadline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feedbacks_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'why_created': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'core.delivery': {
            'Meta': {'ordering': "['-time_of_delivery']", 'object_name': 'Delivery'},
            'alias_delivery': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Delivery']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'copy_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'copies'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Delivery']"}),
            'deadline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deliveries'", 'to': "orm['core.Deadline']"}),
            'delivered_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Candidate']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'delivery_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_feedback': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'latest_feedback_for_delivery'", 'unique': 'True', 'null': 'True', 'to': "orm['core.StaticFeedback']"}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'successful': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'time_of_delivery': ('django.db.models.fields.DateTimeField', [], {})
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
        'core.staticfeedback': {
            'Meta': {'ordering': "['-save_timestamp']", 'object_name': 'StaticFeedback'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feedbacks'", 'to': "orm['core.Delivery']"}),
            'grade': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_passing_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rendered_view': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'save_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'saved_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        'devilry_detektor.comparetwocacheitem': {
            'Meta': {'object_name': 'CompareTwoCacheItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparetwo_cacheitems'", 'to': "orm['devilry_detektor.DetektorAssignmentCacheLanguage']"}),
            'parseresult1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['devilry_detektor.DetektorDeliveryParseResult']"}),
            'parseresult2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['devilry_detektor.DetektorDeliveryParseResult']"}),
            'scaled_points': ('django.db.models.fields.IntegerField', [], {}),
            'summary_json': ('django.db.models.fields.TextField', [], {})
        },
        'devilry_detektor.detektorassignment': {
            'Meta': {'object_name': 'DetektorAssignment'},
            'assignment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Assignment']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_started_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'processing_started_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unprocessed'", 'max_length': '12'})
        },
        'devilry_detektor.detektorassignmentcachelanguage': {
            'Meta': {'ordering': "['language']", 'unique_together': "[('detektorassignment', 'language')]", 'object_name': 'DetektorAssignmentCacheLanguage'},
            'detektorassignment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cachelanguages'", 'to': "orm['devilry_detektor.DetektorAssignment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'devilry_detektor.detektordeliveryparseresult': {
            'Meta': {'unique_together': "[('delivery', 'language')]", 'object_name': 'DetektorDeliveryParseResult'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Delivery']"}),
            'detektorassignment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parseresults'", 'to': "orm['devilry_detektor.DetektorAssignment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords_string': ('django.db.models.fields.TextField', [], {}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'normalized_sourcecode': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_keywords': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_operators': ('django.db.models.fields.IntegerField', [], {}),
            'operators_and_keywords_string': ('django.db.models.fields.TextField', [], {}),
            'operators_string': ('django.db.models.fields.TextField', [], {}),
            'parsed_functions_json': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['devilry_detektor']