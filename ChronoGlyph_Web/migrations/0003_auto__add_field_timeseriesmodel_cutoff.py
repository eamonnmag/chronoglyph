# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TimeSeriesModel.cutoff'
        db.add_column(u'ChronoGlyph_Web_timeseriesmodel', 'cutoff',
                      self.gf('django.db.models.fields.IntegerField')(default=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TimeSeriesModel.cutoff'
        db.delete_column(u'ChronoGlyph_Web_timeseriesmodel', 'cutoff')


    models = {
        u'ChronoGlyph_Web.timeseriescollection': {
            'Meta': {'object_name': 'TimeSeriesCollection'},
            'collection_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ChronoGlyph_Web.TimeSeriesRawFile']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'ChronoGlyph_Web.timeseriesmodel': {
            'Meta': {'object_name': 'TimeSeriesModel'},
            'alphabet_size': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'cutoff': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'network_file': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/outputs/'", 'max_length': '100', 'recursive': 'True'}),
            'parallel_coords_file': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/outputs/'", 'max_length': '100', 'recursive': 'True'}),
            'time_series_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ChronoGlyph_Web.TimeSeriesCollection']"}),
            'time_series_file': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/outputs/'", 'max_length': '100', 'recursive': 'True'}),
            'window_size': ('django.db.models.fields.IntegerField', [], {'default': '4'})
        },
        u'ChronoGlyph_Web.timeseriesprocessedfile': {
            'Meta': {'object_name': 'TimeSeriesProcessedFile'},
            'file_path': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/eamonnmaguire/git/ovii/ChronoGlyph/ChronoGlyph_Web/timeseries_analysis/datasets/outputs/'", 'max_length': '100', 'recursive': 'True'}),
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