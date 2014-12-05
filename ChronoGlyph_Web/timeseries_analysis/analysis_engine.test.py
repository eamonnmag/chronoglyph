import unittest
from datetime import datetime
from ChronoGlyph_Web.models import TimeSeriesModel
from ChronoGlyph_Web.timeseries_analysis.analysis_engine import AnalysisEngine
from ChronoGlyph_Web.views import get_collection_by_id

__author__ = 'eamonnmaguire'


class TestAnalysisEngine(unittest.TestCase):
    def setUp(self):
        self.analysis_engine = AnalysisEngine()

    def test_benchmark(self):

        collections = ['ECG', 'ECG_SP', 'ECG_1', 'SPACE']
        algorithms = ['max_repeats', 'bound_sliding_window', 'max_repeats_compressed']

        ts_file = open("output_summary.txt", 'w')

        alphabet_size = 3
        while alphabet_size < 10:
            window_size = 5
            while window_size < 25:

                for collection in collections:
                    collection_model_item = get_collection_by_id(collection)
                    for algorithm in algorithms:
                        model_name = collection + "-" \
                                     + algorithm + "-" + str(window_size) + "-" + str(alphabet_size)

                        if algorithm == 'bound_sliding_window':
                            segment_size = 15
                            while segment_size < 60:
                                self.benchmark(model_name + '-ss' + str(segment_size), collection_model_item, algorithm,
                                               window_size, alphabet_size,
                                               segment_size, ts_file)
                                segment_size += 10
                        else:
                            self.benchmark(model_name, collection_model_item, algorithm, window_size, alphabet_size,
                                           1, ts_file)

                window_size += 5
            alphabet_size += 1

        ts_file.close()


    def benchmark(self, model_name, collection, algorithm, window_size, alphabet_size, segment_size, ts_file):

        analysis_model = TimeSeriesModel(model_name=model_name, window_size=window_size, alphabet_size=alphabet_size,
                                         cutoff=1, algorithm=algorithm, algorithm_parameter=segment_size,
                                         time_series_collection=collection)

        analysis_model.save()

        start_time = datetime.now()
        (num_motifs, total_values) = self.analysis_engine.run_analysis(analysis_model, output_files=False)

        total_time = (datetime.now() - start_time)
        total_milliseconds = int(total_time.total_seconds() * 1000)
        print 'Analysing ' + collection.collection_id + ' with ' + algorithm + ' (w=' + window_size + ', a=' + alphabet_size + ') took ' + str(
            total_milliseconds) + ' ms'

        ts_file.write(
            collection.collection_id + "\t" + model_name + "\t" + str(total_values) + "\t" + algorithm + "\t" + str(
                window_size) + "\t" + str(alphabet_size) + "\t" + str(segment_size) + "\t" + str(
                total_milliseconds) + "\t" + str(num_motifs) + "\n")


