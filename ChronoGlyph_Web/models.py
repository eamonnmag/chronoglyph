from django.db import models

# Create your models here.
from ChronoGlyph.settings import OUTPUT_DIR, DATA_DIR


class TimeSeriesRawFile(models.Model):
    name = models.CharField(max_length=256)
    location = models.FilePathField(path=DATA_DIR, recursive=True)

    def __unicode__(self):
        return self.name


class TimeSeriesCollection(models.Model):
    collection_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.TextField()

    files = models.ManyToManyField(TimeSeriesRawFile)

    def __unicode__(self):
        return self.name


class TimeSeriesProcessedFile(models.Model):
    """
    Represents the files that have been created for display in the UI (for rickshaft for example)
    """
    name = models.CharField(max_length=256)
    file_path = models.FilePathField(path=OUTPUT_DIR, recursive=True)


class TimeSeriesModel(models.Model):
    """
    Stores the analysis of the time series so that it can be recovered instead of having to process everything again
    """
    model_name = models.CharField(max_length=256)
    window_size = models.IntegerField(default=4)
    alphabet_size = models.IntegerField(default=4)
    cutoff = models.IntegerField(default=2)

    algorithm = models.CharField(max_length=256, default='Maximal Repeats')
    algorithm_parameter = models.IntegerField(default=5)

    time_series_collection = models.ForeignKey(TimeSeriesCollection)

    parallel_coords_file = models.FilePathField(path=OUTPUT_DIR, recursive=True)
    network_file = models.FilePathField(path=OUTPUT_DIR, recursive=True)
    time_series_file = models.FilePathField(path=OUTPUT_DIR, recursive=True)

    def __unicode__(self):
        return self.model_name