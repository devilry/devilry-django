# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AssignmentGroup.feedback'
        db.alter_column('core_assignmentgroup', 'feedback_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.StaticFeedback'], unique=True, null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):

        # Changing field 'AssignmentGroup.feedback'
        db.alter_column('core_assignmentgroup', 'feedback_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.StaticFeedback'], unique=True, null=True))

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
            'feedback': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.StaticFeedback']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_deadline': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_deadline_for_group'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Deadline']", 'blank': 'True', 'unique': 'True'}),
            'last_delivery': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'last_delivery_by_group'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Delivery']", 'blank': 'True', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignmentgroups'", 'to': "orm['core.Assignment']"})
        },
        'core.assignmentgrouptag': {
            'Meta': {'ordering': "['tag']", 'unique_together': "(('assignment_group', 'tag'),)", 'object_name': 'AssignmentGroupTag'},
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'to': "orm['core.AssignmentGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
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
        'core.devilryuserprofile': {
            'Meta': {'object_name': 'DevilryUserProfile'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'core.examiner': {
            'Meta': {'unique_together': "(('user', 'assignmentgroup'),)", 'object_name': 'Examiner', 'db_table': "'core_assignmentgroup_examiners'"},
            'assignmentgroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'examiners'", 'to': "orm['core.AssignmentGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.filemeta': {
            'Meta': {'ordering': "['filename']", 'unique_together': "(('delivery', 'filename'),)", 'object_name': 'FileMeta'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filemetas'", 'to': "orm['core.Delivery']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.groupinvite': {
            'Meta': {'object_name': 'GroupInvite'},
            'accepted': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.AssignmentGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responded_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sent_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groupinvite_sent_by_set'", 'to': "orm['auth.User']"}),
            'sent_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sent_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groupinvite_sent_to_set'", 'to': "orm['auth.User']"})
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
        'core.periodapplicationkeyvalue': {
            'Meta': {'unique_together': "(('period', 'application', 'key'),)", 'object_name': 'PeriodApplicationKeyValue'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Period']"}),
            'value': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'core.pointrangetograde': {
            'Meta': {'ordering': "['minimum_points']", 'unique_together': "(('point_to_grade_map', 'grade'),)", 'object_name': 'PointRangeToGrade'},
            'grade': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'minimum_points': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'point_to_grade_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.PointToGradeMap']"})
        },
        'core.pointtogrademap': {
            'Meta': {'object_name': 'PointToGradeMap'},
            'assignment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Assignment']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'core.relatedexaminer': {
            'Meta': {'unique_together': "(('period', 'user'),)", 'object_name': 'RelatedExaminer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Period']"}),
            'tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.relatedstudent': {
            'Meta': {'unique_together': "(('period', 'user'),)", 'object_name': 'RelatedStudent'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Period']"}),
            'tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.relatedstudentkeyvalue': {
            'Meta': {'unique_together': "(('relatedstudent', 'application', 'key'),)", 'object_name': 'RelatedStudentKeyValue'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'}),
            'relatedstudent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.RelatedStudent']"}),
            'student_can_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['core']