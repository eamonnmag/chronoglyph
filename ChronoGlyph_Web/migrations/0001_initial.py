# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TimeSeriesRawFile'
        db.create_table(u'ChronoGlyph_Web_timeseriesrawfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('location', self.gf('django.db.models.fields.FilePathField')(path='/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/', max_length=100, recursive=True)),
        ))
        db.send_create_signal(u'ChronoGlyph_Web', ['TimeSeriesRawFile'])

        # Adding model 'TimeSeriesCollection'
        db.create_table(u'ChronoGlyph_Web_timeseriescollection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ChronoGlyph_Web', ['TimeSeriesCollection'])

        # Adding M2M table for field files on 'TimeSeriesCollection'
        m2m_table_name = db.shorten_name(u'ChronoGlyph_Web_timeseriescollection_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timeseriescollection', models.ForeignKey(orm[u'ChronoGlyph_Web.timeseriescollection'], null=False)),
            ('timeseriesrawfile', models.ForeignKey(orm[u'ChronoGlyph_Web.timeseriesrawfile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['timeseriescollection_id', 'timeseriesrawfile_id'])

        # Adding model 'TimeSeriesProcessedFile'
        db.create_table(u'ChronoGlyph_Web_timeseriesprocessedfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('file_path', self.gf('django.db.models.fields.FilePathField')(path='/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/', max_length=100, recursive=True)),
        ))
        db.send_create_signal(u'ChronoGlyph_Web', ['TimeSeriesProcessedFile'])

        # Adding model 'TimeSeriesAnalysis'
        db.create_table(u'ChronoGlyph_Web_timeseriesanalysis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('window_size', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('alphabet_size', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('time_series_collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ChronoGlyph_Web.TimeSeriesCollection'])),
            ('feature_summary_file', self.gf('django.db.models.fields.FilePathField')(path='/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/', max_length=100, recursive=True)),
            ('distance_network', self.gf('django.db.models.fields.FilePathField')(path='/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/', max_length=100, recursive=True)),
        ))
        db.send_create_signal(u'ChronoGlyph_Web', ['TimeSeriesAnalysis'])

        # Adding M2M table for field processed_series on 'TimeSeriesAnalysis'
        m2m_table_name = db.shorten_name(u'ChronoGlyph_Web_timeseriesanalysis_processed_series')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timeseriesanalysis', models.ForeignKey(orm[u'ChronoGlyph_Web.timeseriesanalysis'], null=False)),
            ('timeseriesprocessedfile', models.ForeignKey(orm[u'ChronoGlyph_Web.timeseriesprocessedfile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['timeseriesanalysis_id', 'timeseriesprocessedfile_id'])


    def backwards(self, orm):
        # Deleting model 'TimeSeriesRawFile'
        db.delete_table(u'ChronoGlyph_Web_timeseriesrawfile')

        # Deleting model 'TimeSeriesCollection'
        db.delete_table(u'ChronoGlyph_Web_timeseriescollection')

        # Removing M2M table for field files on 'TimeSeriesCollection'
        db.delete_table(db.shorten_name(u'ChronoGlyph_Web_timeseriescollection_files'))

        # Deleting model 'TimeSeriesProcessedFile'
        db.delete_table(u'ChronoGlyph_Web_timeseriesprocessedfile')

        # Deleting model 'TimeSeriesAnalysis'
        db.delete_table(u'ChronoGlyph_Web_timeseriesanalysis')

        # Removing M2M table for field processed_series on 'TimeSeriesAnalysis'
        db.delete_table(db.shorten_name(u'ChronoGlyph_Web_timeseriesanalysis_processed_series'))


    models = {
        u'ChronoGlyph_Web.timeseriesanalysis': {
            'Meta': {'object_name': 'TimeSeriesAnalysis'},
            'alphabet_size': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'distance_network': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/'", 'max_length': '100', 'recursive': 'True'}),
            'feature_summary_file': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/'", 'max_length': '100', 'recursive': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'processed_series': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ChronoGlyph_Web.TimeSeriesProcessedFile']", 'symmetrical': 'False'}),
            'time_series_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ChronoGlyph_Web.TimeSeriesCollection']"}),
            'window_size': ('django.db.models.fields.IntegerField', [], {'default': '4'})
        },
        u'ChronoGlyph_Web.timeseriescollection': {
            'Meta': {'object_name': 'TimeSeriesCollection'},
            'collection_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ChronoGlyph_Web.TimeSeriesRawFile']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'ChronoGlyph_Web.timeseriesprocessedfile': {
            'Meta': {'object_name': 'TimeSeriesProcessedFile'},
            'file_path': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/'", 'max_length': '100', 'recursive': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'ChronoGlyph_Web.timeseriesrawfile': {
            'Meta': {'object_name': 'TimeSeriesRawFile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/'", 'max_length': '100', 'recursive': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['ChronoGlyph_Web']