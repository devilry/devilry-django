# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedbackDraftFile'
        db.create_table(u'devilry_gradingsystem_feedbackdraftfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['core.Delivery'])),
            ('saved_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'devilry_gradingsystem', ['FeedbackDraftFile'])


    def backwards(self, orm):
        # Deleting model 'FeedbackDraftFile'
        db.delete_table(u'devilry_gradingsystem_feedbackdraftfile')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.assignment': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Assignment'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadline_handling': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'delivery_types': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'examiners_publish_feedbacks_directly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'first_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'grading_system_plugin_id': ('django.db.models.fields.CharField', [], {'default': "'devilry_gradingsystemplugin_approved'", 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'feedback': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.StaticFeedback']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_deadline': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_deadline_for_group'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Deadline']", 'blank': 'True', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignmentgroups'", 'to': "orm['core.Assignment']"})
        },
        'core.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'candidates'", 'to': "orm['core.AssignmentGroup']"}),
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'core.deadline': {
            'Meta': {'ordering': "['-deadline']", 'object_name': 'Deadline'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deadlines'", 'to': "orm['core.AssignmentGroup']"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'deliveries_available_before_deadline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feedbacks_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_feedback': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'latest_feedback_for_delivery'", 'unique': 'True', 'null': 'True', 'to': "orm['core.StaticFeedback']"}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'successful': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'time_of_delivery': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'core.node': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Node'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_nodes'", 'null': 'True', 'to': "orm['core.Node']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'})
        },
        'core.period': {
            'Meta': {'ordering': "['short_name']", 'unique_together': "(('short_name', 'parentnode'),)", 'object_name': 'Period'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periods'", 'to': "orm['core.Subject']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.staticfeedback': {
            'Meta': {'ordering': "['-save_timestamp']", 'object_name': 'StaticFeedback'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feedbacks'", 'to': "orm['core.Delivery']"}),
            'grade': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_passing_grade': ('django.db.models.fields.BooleanField', [], {}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rendered_view': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'save_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'saved_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'core.subject': {
            'Meta': {'ordering': "['short_name']", 'object_name': 'Subject'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': "orm['core.Node']"}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'devilry_gradingsystem.feedbackdraft': {
            'Meta': {'ordering': "['-save_timestamp']", 'object_name': 'FeedbackDraft'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devilry_gradingsystem_feedbackdraft_set'", 'to': "orm['core.Delivery']"}),
            'feedbacktext_editor': ('django.db.models.fields.CharField', [], {'default': "'devilry-markdown'", 'max_length': "'20'"}),
            'feedbacktext_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feedbacktext_raw': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'save_timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'saved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devilry_gradingsystem_feedbackdraft_set'", 'to': u"orm['auth.User']"}),
            'staticfeedback': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'devilry_gradingsystem_feedbackdraft_set'", 'unique': 'True', 'null': 'True', 'to': "orm['core.StaticFeedback']"})
        },
        u'devilry_gradingsystem.feedbackdraftfile': {
            'Meta': {'object_name': 'FeedbackDraftFile'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['core.Delivery']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'saved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['devilry_gradingsystem']