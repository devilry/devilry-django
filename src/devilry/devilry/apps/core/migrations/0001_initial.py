# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Node'
        db.create_table('core_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('devilry.apps.core.models.custom_db_fields.ShortNameField')(max_length=20)),
            ('long_name', self.gf('devilry.apps.core.models.custom_db_fields.LongNameField')(max_length=100, db_index=True)),
            ('parentnode', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_nodes', null=True, to=orm['core.Node'])),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('core', ['Node'])

        # Adding unique constraint on 'Node', fields ['short_name', 'parentnode']
        db.create_unique('core_node', ['short_name', 'parentnode_id'])

        # Adding M2M table for field admins on 'Node'
        m2m_table_name = db.shorten_name('core_node_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('node', models.ForeignKey(orm['core.node'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['node_id', 'user_id'])

        # Adding model 'Subject'
        db.create_table('core_subject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('devilry.apps.core.models.custom_db_fields.ShortNameField')(unique=True, max_length=20)),
            ('long_name', self.gf('devilry.apps.core.models.custom_db_fields.LongNameField')(max_length=100, db_index=True)),
            ('parentnode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subjects', to=orm['core.Node'])),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['Subject'])

        # Adding M2M table for field admins on 'Subject'
        m2m_table_name = db.shorten_name('core_subject_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subject', models.ForeignKey(orm['core.subject'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['subject_id', 'user_id'])

        # Adding model 'Period'
        db.create_table('core_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('devilry.apps.core.models.custom_db_fields.ShortNameField')(max_length=20)),
            ('long_name', self.gf('devilry.apps.core.models.custom_db_fields.LongNameField')(max_length=100, db_index=True)),
            ('parentnode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='periods', to=orm['core.Subject'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['Period'])

        # Adding unique constraint on 'Period', fields ['short_name', 'parentnode']
        db.create_unique('core_period', ['short_name', 'parentnode_id'])

        # Adding M2M table for field admins on 'Period'
        m2m_table_name = db.shorten_name('core_period_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('period', models.ForeignKey(orm['core.period'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['period_id', 'user_id'])

        # Adding model 'PeriodApplicationKeyValue'
        db.create_table('core_periodapplicationkeyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.CharField')(max_length=300, db_index=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=300, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(db_index=True, null=True, blank=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Period'])),
        ))
        db.send_create_signal('core', ['PeriodApplicationKeyValue'])

        # Adding unique constraint on 'PeriodApplicationKeyValue', fields ['period', 'application', 'key']
        db.create_unique('core_periodapplicationkeyvalue', ['period_id', 'application', 'key'])

        # Adding model 'RelatedExaminer'
        db.create_table('core_relatedexaminer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Period'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tags', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['RelatedExaminer'])

        # Adding unique constraint on 'RelatedExaminer', fields ['period', 'user']
        db.create_unique('core_relatedexaminer', ['period_id', 'user_id'])

        # Adding model 'RelatedStudent'
        db.create_table('core_relatedstudent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Period'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tags', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('candidate_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['RelatedStudent'])

        # Adding unique constraint on 'RelatedStudent', fields ['period', 'user']
        db.create_unique('core_relatedstudent', ['period_id', 'user_id'])

        # Adding model 'RelatedStudentKeyValue'
        db.create_table('core_relatedstudentkeyvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.CharField')(max_length=300, db_index=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=300, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(db_index=True, null=True, blank=True)),
            ('relatedstudent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.RelatedStudent'])),
            ('student_can_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['RelatedStudentKeyValue'])

        # Adding unique constraint on 'RelatedStudentKeyValue', fields ['relatedstudent', 'application', 'key']
        db.create_unique('core_relatedstudentkeyvalue', ['relatedstudent_id', 'application', 'key'])

        # Adding model 'DevilryUserProfile'
        db.create_table('core_devilryuserprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['DevilryUserProfile'])

        # Adding model 'Candidate'
        db.create_table('core_candidate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('assignment_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='candidates', to=orm['core.AssignmentGroup'])),
            ('candidate_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['Candidate'])

        # Adding model 'Assignment'
        db.create_table('core_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('devilry.apps.core.models.custom_db_fields.ShortNameField')(max_length=20)),
            ('long_name', self.gf('devilry.apps.core.models.custom_db_fields.LongNameField')(max_length=100, db_index=True)),
            ('parentnode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assignments', to=orm['core.Period'])),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('publishing_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('anonymous', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('students_can_see_points', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('examiners_publish_feedbacks_directly', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delivery_types', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('deadline_handling', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('scale_points_percent', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('first_deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Assignment'])

        # Adding unique constraint on 'Assignment', fields ['short_name', 'parentnode']
        db.create_unique('core_assignment', ['short_name', 'parentnode_id'])

        # Adding M2M table for field admins on 'Assignment'
        m2m_table_name = db.shorten_name('core_assignment_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assignment', models.ForeignKey(orm['core.assignment'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['assignment_id', 'user_id'])

        # Adding model 'AssignmentGroup'
        db.create_table('core_assignmentgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parentnode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assignmentgroups', to=orm['core.Assignment'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('feedback', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.StaticFeedback'], unique=True, null=True, blank=True)),
            ('etag', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['AssignmentGroup'])

        # Adding model 'AssignmentGroupTag'
        db.create_table('core_assignmentgrouptag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assignment_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', to=orm['core.AssignmentGroup'])),
            ('tag', self.gf('django.db.models.fields.SlugField')(max_length=20)),
        ))
        db.send_create_signal('core', ['AssignmentGroupTag'])

        # Adding unique constraint on 'AssignmentGroupTag', fields ['assignment_group', 'tag']
        db.create_unique('core_assignmentgrouptag', ['assignment_group_id', 'tag'])

        # Adding model 'Deadline'
        db.create_table('core_deadline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assignment_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deadlines', to=orm['core.AssignmentGroup'])),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('deliveries_available_before_deadline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feedbacks_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Deadline'])

        # Adding model 'FileMeta'
        db.create_table('core_filemeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(related_name='filemetas', to=orm['core.Delivery'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('core', ['FileMeta'])

        # Adding unique constraint on 'FileMeta', fields ['delivery', 'filename']
        db.create_unique('core_filemeta', ['delivery_id', 'filename'])

        # Adding model 'Delivery'
        db.create_table('core_delivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery_type', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('time_of_delivery', self.gf('django.db.models.fields.DateTimeField')()),
            ('deadline', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deliveries', to=orm['core.Deadline'])),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('successful', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivered_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Candidate'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('alias_delivery', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Delivery'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('copy_of', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='copies', null=True, on_delete=models.SET_NULL, to=orm['core.Delivery'])),
        ))
        db.send_create_signal('core', ['Delivery'])

        # Adding model 'StaticFeedback'
        db.create_table('core_staticfeedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(related_name='feedbacks', to=orm['core.Delivery'])),
            ('rendered_view', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('grade', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('points', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_passing_grade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('save_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('saved_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('core', ['StaticFeedback'])

        # Adding model 'Examiner'
        db.create_table('core_assignmentgroup_examiners', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('assignmentgroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='examiners', to=orm['core.AssignmentGroup'])),
        ))
        db.send_create_signal('core', ['Examiner'])

        # Adding unique constraint on 'Examiner', fields ['user', 'assignmentgroup']
        db.create_unique('core_assignmentgroup_examiners', ['user_id', 'assignmentgroup_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Examiner', fields ['user', 'assignmentgroup']
        db.delete_unique('core_assignmentgroup_examiners', ['user_id', 'assignmentgroup_id'])

        # Removing unique constraint on 'FileMeta', fields ['delivery', 'filename']
        db.delete_unique('core_filemeta', ['delivery_id', 'filename'])

        # Removing unique constraint on 'AssignmentGroupTag', fields ['assignment_group', 'tag']
        db.delete_unique('core_assignmentgrouptag', ['assignment_group_id', 'tag'])

        # Removing unique constraint on 'Assignment', fields ['short_name', 'parentnode']
        db.delete_unique('core_assignment', ['short_name', 'parentnode_id'])

        # Removing unique constraint on 'RelatedStudentKeyValue', fields ['relatedstudent', 'application', 'key']
        db.delete_unique('core_relatedstudentkeyvalue', ['relatedstudent_id', 'application', 'key'])

        # Removing unique constraint on 'RelatedStudent', fields ['period', 'user']
        db.delete_unique('core_relatedstudent', ['period_id', 'user_id'])

        # Removing unique constraint on 'RelatedExaminer', fields ['period', 'user']
        db.delete_unique('core_relatedexaminer', ['period_id', 'user_id'])

        # Removing unique constraint on 'PeriodApplicationKeyValue', fields ['period', 'application', 'key']
        db.delete_unique('core_periodapplicationkeyvalue', ['period_id', 'application', 'key'])

        # Removing unique constraint on 'Period', fields ['short_name', 'parentnode']
        db.delete_unique('core_period', ['short_name', 'parentnode_id'])

        # Removing unique constraint on 'Node', fields ['short_name', 'parentnode']
        db.delete_unique('core_node', ['short_name', 'parentnode_id'])

        # Deleting model 'Node'
        db.delete_table('core_node')

        # Removing M2M table for field admins on 'Node'
        db.delete_table(db.shorten_name('core_node_admins'))

        # Deleting model 'Subject'
        db.delete_table('core_subject')

        # Removing M2M table for field admins on 'Subject'
        db.delete_table(db.shorten_name('core_subject_admins'))

        # Deleting model 'Period'
        db.delete_table('core_period')

        # Removing M2M table for field admins on 'Period'
        db.delete_table(db.shorten_name('core_period_admins'))

        # Deleting model 'PeriodApplicationKeyValue'
        db.delete_table('core_periodapplicationkeyvalue')

        # Deleting model 'RelatedExaminer'
        db.delete_table('core_relatedexaminer')

        # Deleting model 'RelatedStudent'
        db.delete_table('core_relatedstudent')

        # Deleting model 'RelatedStudentKeyValue'
        db.delete_table('core_relatedstudentkeyvalue')

        # Deleting model 'DevilryUserProfile'
        db.delete_table('core_devilryuserprofile')

        # Deleting model 'Candidate'
        db.delete_table('core_candidate')

        # Deleting model 'Assignment'
        db.delete_table('core_assignment')

        # Removing M2M table for field admins on 'Assignment'
        db.delete_table(db.shorten_name('core_assignment_admins'))

        # Deleting model 'AssignmentGroup'
        db.delete_table('core_assignmentgroup')

        # Deleting model 'AssignmentGroupTag'
        db.delete_table('core_assignmentgrouptag')

        # Deleting model 'Deadline'
        db.delete_table('core_deadline')

        # Deleting model 'FileMeta'
        db.delete_table('core_filemeta')

        # Deleting model 'Delivery'
        db.delete_table('core_delivery')

        # Deleting model 'StaticFeedback'
        db.delete_table('core_staticfeedback')

        # Deleting model 'Examiner'
        db.delete_table('core_assignmentgroup_examiners')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('devilry.apps.core.models.custom_db_fields.LongNameField', [], {'max_length': '100', 'db_index': 'True'}),
            'parentnode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['core.Period']"}),
            'publishing_time': ('django.db.models.fields.DateTimeField', [], {}),
            'scale_points_percent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'short_name': ('devilry.apps.core.models.custom_db_fields.ShortNameField', [], {'max_length': '20'}),
            'students_can_see_points': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'core.assignmentgroup': {
            'Meta': {'ordering': "['id']", 'object_name': 'AssignmentGroup'},
            'etag': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.StaticFeedback']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'assignment_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deadlines'", 'to': "orm['core.AssignmentGroup']"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'deliveries_available_before_deadline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feedbacks_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.delivery': {
            'Meta': {'ordering': "['-time_of_delivery']", 'object_name': 'Delivery'},
            'alias_delivery': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Delivery']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'copy_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'copies'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['core.Delivery']"}),
            'deadline': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deliveries'", 'to': "orm['core.Deadline']"}),
            'delivered_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Candidate']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'delivery_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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