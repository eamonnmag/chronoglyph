from django.contrib import admin

# Register your models here.
from ChronoGlyph_Web.models import TimeSeriesCollection, TimeSeriesRawFile, TimeSeriesProcessedFile, \
    TimeSeriesModel

admin.site.register(TimeSeriesRawFile)
admin.site.register(TimeSeriesCollection)
admin.site.register(TimeSeriesProcessedFile)
admin.site.register(TimeSeriesModel)