# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Terminal'
        db.create_table(u'product_test_terminal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'product_test', ['Terminal'])

        # Adding model 'Device'
        db.create_table(u'product_test_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('terminal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product_test.Terminal'])),
            ('port_id', self.gf('django.db.models.fields.IntegerField')()),
            ('sn', self.gf('django.db.models.fields.CharField')(default='', max_length=16)),
            ('mac', self.gf('django.db.models.fields.CharField')(default='', max_length=14)),
            ('state', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'product_test', ['Device'])

        # Adding model 'Pool'
        db.create_table(u'product_test_pool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('platform', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('hw', self.gf('django.db.models.fields.CharField')(default='', max_length=4)),
            ('image', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('bootloader', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('sysloader', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('state', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cpld', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('job', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
        ))
        db.send_create_signal(u'product_test', ['Pool'])

        # Adding model 'License'
        db.create_table(u'product_test_license', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('deadline', self.gf('django.db.models.fields.CharField')(default='', max_length=35)),
            ('username', self.gf('django.db.models.fields.CharField')(default='', max_length=35)),
        ))
        db.send_create_signal(u'product_test', ['License'])

        # Adding model 'Task'
        db.create_table(u'product_test_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('platform', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('hw', self.gf('django.db.models.fields.CharField')(default='', max_length=4)),
            ('image', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('bootloader', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('sysloader', self.gf('django.db.models.fields.CharField')(default='', max_length=40)),
            ('cpld', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('begin', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('over', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('history', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'product_test', ['Task'])

        # Adding model 'Subtask'
        db.create_table(u'product_test_subtask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product_test.Task'])),
            ('terminal', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(default='0.0.0.0', max_length=15)),
            ('port_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sn', self.gf('django.db.models.fields.CharField')(default='', max_length=16)),
            ('mac', self.gf('django.db.models.fields.CharField')(default='', max_length=12)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('log', self.gf('django.db.models.fields.TextField')()),
            ('console_log', self.gf('django.db.models.fields.TextField')()),
            ('prompt', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
        ))
        db.send_create_signal(u'product_test', ['Subtask'])

        # Adding model 'Script'
        db.create_table(u'product_test_script', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('files', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'product_test', ['Script'])

        # Adding model 'Platform'
        db.create_table(u'product_test_platform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('script', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product_test.Script'])),
            ('serial', self.gf('django.db.models.fields.CharField')(default='', max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('memory', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
        ))
        db.send_create_signal(u'product_test', ['Platform'])


    def backwards(self, orm):
        # Deleting model 'Terminal'
        db.delete_table(u'product_test_terminal')

        # Deleting model 'Device'
        db.delete_table(u'product_test_device')

        # Deleting model 'Pool'
        db.delete_table(u'product_test_pool')

        # Deleting model 'License'
        db.delete_table(u'product_test_license')

        # Deleting model 'Task'
        db.delete_table(u'product_test_task')

        # Deleting model 'Subtask'
        db.delete_table(u'product_test_subtask')

        # Deleting model 'Script'
        db.delete_table(u'product_test_script')

        # Deleting model 'Platform'
        db.delete_table(u'product_test_platform')


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
        u'product_test.device': {
            'Meta': {'object_name': 'Device'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '14'}),
            'port_id': ('django.db.models.fields.IntegerField', [], {}),
            'sn': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16'}),
            'state': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terminal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product_test.Terminal']"})
        },
        u'product_test.license': {
            'Meta': {'object_name': 'License'},
            'deadline': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '35'})
        },
        u'product_test.platform': {
            'Meta': {'object_name': 'Platform'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product_test.Script']"}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'})
        },
        u'product_test.pool': {
            'Meta': {'object_name': 'Pool'},
            'bootloader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'cpld': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'hw': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'job': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'state': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sysloader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'product_test.script': {
            'Meta': {'object_name': 'Script'},
            'files': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        u'product_test.subtask': {
            'Meta': {'object_name': 'Subtask'},
            'console_log': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'default': "'0.0.0.0'", 'max_length': '15'}),
            'log': ('django.db.models.fields.TextField', [], {}),
            'mac': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12'}),
            'port_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'prompt': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sn': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product_test.Task']"}),
            'terminal': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        u'product_test.task': {
            'Meta': {'object_name': 'Task'},
            'begin': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'bootloader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'cpld': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'history': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hw': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'over': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sysloader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40'})
        },
        u'product_test.terminal': {
            'Meta': {'object_name': 'Terminal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['product_test']