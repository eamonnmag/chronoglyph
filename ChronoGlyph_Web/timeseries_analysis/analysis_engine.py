import re
from datetime import datetime
import numpy
import simplejson
from ChronoGlyph.settings import OUTPUT_DIR
from ChronoGlyph_Web.timeseries_analysis.max_repeats.rstr_max import Rstr_max
from ChronoGlyph_Web.timeseries_analysis.sax import saxpy
import scipy
import scipy.stats
from ChronoGlyph_Web.timeseries_analysis.string_processing.normalized_sequence_analysis import \
    NormalizedSequenceAnalysis
from ChronoGlyph_Web.timeseries_analysis.string_processing.sliding_window_impl import SlidingWindowAnalysis

__author__ = 'eamonnmaguire'


class AnalysisEngine(object):
    def add_ngram_to_aggregated_sets(self, aggregated_sets, metrics, file_id, items, time_series, window_size, mapping):
        occurrences = {}

        # w_s = minimum space required for distinct visualization of point in time series
        w_s = 2
        # w_g = glyph width in the display - helps us calculate how much space can be saved
        w_g = 40
        swa = NormalizedSequenceAnalysis()

        for position_key in items:
            ngram = items[position_key]["ngram"]

            approximation = ngram["symbolic_approximation"]
            if not approximation[0].isdigit():
                actual_approximation = approximation

                if mapping is not None:
                    # extend approximation
                    # checking here to ensure position key is not modified
                    approximation = swa.expand_numeric_approximation(0, ngram["symbolic_approximation"],
                                                                     mapping["compressed_count_mapping"])

                    actual_approximation = swa.extend_approximation(0, ngram["symbolic_approximation"],
                                                                    mapping["count_mapping"])

                if len(approximation) > 1:
                    if not approximation in aggregated_sets:
                        aggregated_sets[approximation] = {"id": len(aggregated_sets),
                                                          "approximation": approximation,
                                                          "count": 0, "metrics": [], "series": []}
                    if not approximation in occurrences:
                        occurrences[approximation] = {}

                    aggregated_sets[approximation]["count"] += 1

                    if not file_id in occurrences[approximation]:
                        occurrences[approximation][file_id] = []

                    if not approximation in metrics:
                        metrics[approximation] = []
                        # now calculate the stats for this motif given the context area...

                    series_slice = time_series[
                                   int(position_key) * window_size: (int(position_key) + len(
                                       actual_approximation)) * window_size]
                    if len(series_slice) > 0:
                        series_metric = {
                            "Kurtosis": round(scipy.stats.kurtosis(series_slice, fisher=False, bias=False), 3),
                            "Skewedness": round(scipy.stats.skew(series_slice, bias=False), 3),
                            "Length": round(len(actual_approximation), 3),
                            "Max": round(numpy.max(series_slice), 3),
                            "Min": round(numpy.min(series_slice), 3),
                            "Mean": round(scipy.stats.nanmean(series_slice), 3),
                            "Median": round(scipy.stats.nanmedian(series_slice), 3),
                            "Deviation": round(scipy.stats.nanstd(series_slice), 3),
                            "Std Error": round(scipy.stats.sem(series_slice), 3),
                            "Pixel Saving Ptnl": round((w_s * len(actual_approximation) * window_size) / w_g,
                                                       3),
                            "Compression Ptnl.": round((len(actual_approximation) * window_size *
                                                        aggregated_sets[approximation][
                                                            "count"]) / aggregated_sets[approximation][
                                                           "count"], 3),
                            "Volatility": round(
                                scipy.stats.nanstd(series_slice) / scipy.stats.nanmean(series_slice), 3)}

                        occurrences[approximation][file_id].append({"position":
                                                                        [int(position_key) * window_size, (
                                                                            int(position_key) + len(
                                                                                actual_approximation)) * window_size],
                                                                    "metrics": series_metric})
                        metrics[approximation].append(series_metric)

        for approximation in metrics:
            # aggregate the metrics we have, ignoring nans where they exist scipy.stats.nanmean(values)
            metric_values = {}
            for val in metrics[approximation]:
                for key in val:
                    if not (key in metric_values):
                        metric_values[key] = []

                    metric_values[key].append(val[key])

            for metric in metric_values:
                aggregated_sets[approximation]["metrics"].append(
                    {"name": metric, "value": round(scipy.stats.nanmean(metric_values[metric]), 3)})

        for ngram in occurrences:
            aggregated_sets[ngram]["series"].append(
                {"file": file_id, "positions": occurrences[ngram][file_id]})

        return aggregated_sets


    def burstiness(self, series_slice):
        # calculated as in http://www.mitpressjournals.org/doi/pdf/10.1162/089976603322518759
        count = 0
        running_sum = 0
        while count < len(series_slice) - 1:
            running_sum += (3 * scipy.power(series_slice[count] - series_slice[count + 1], 2)) / \
                           scipy.power(series_slice[count] + series_slice[count + 1], 2)
            count += 1

        return (1 / len(series_slice)) * running_sum


    def create_linked_graph(self, aggregated_sets, file, window_size):

        unlinked_graph = {"nodes": [], "links": []}
        for approximation in aggregated_sets:
            unlinked_graph["nodes"].append(aggregated_sets[approximation])

        # graph_file = open(
        # OUTPUT_DIR + file + '_unlinked_graph_' + str(window_size) + '.json', 'w')
        # graph_file.write(simplejson.dumps(unlinked_graph))
        # graph_file.close()
        distance_graph = unlinked_graph
        # we have to do pairwise comparisons -  O(N2)
        count = 1
        seen = []
        for approximation in aggregated_sets:
            for approximation2 in aggregated_sets:
                key_1 = approximation + approximation2
                key_2 = approximation2 + approximation
                if len(approximation) == len(approximation2) and approximation != approximation2 and (
                            not key_1 in seen and not key_2 in seen):
                    distance = self.sax.compare_strings(approximation, approximation2) * 70
                    distance_graph["links"].append({"id": count, "source": aggregated_sets[approximation]["id"],
                                                    "target": aggregated_sets[approximation2]["id"],
                                                    "value": distance})
                    seen.append(key_1)
                    count += 1

        linked_graph_file = OUTPUT_DIR + file + '_distance_graph_' + str(window_size) + '.json'
        graph_file = open(linked_graph_file, 'w')
        graph_file.write(simplejson.dumps(distance_graph))
        graph_file.close()

        return linked_graph_file

    def create_parallel_coords_plot(self, aggregated_sets, model_name, window_size):
        """
        Outputs the parallel coordinate JSON file
        :param aggregated_sets:
        :param count_cut_off:
        :param model_name:
        :param window_size:
        :return:
        """
        par_coords_data = []
        for approximation in aggregated_sets:

            record = {"id": aggregated_sets[approximation]["id"],
                      "Approximation": approximation,
                      "Frequency": aggregated_sets[approximation]["count"]}

            for metric in aggregated_sets[approximation]["metrics"]:
                record[metric["name"]] = metric["value"]

            par_coords_data.append(record)

        parallel_coords_files = OUTPUT_DIR + model_name + '_par_coords_' + str(window_size) + '.json'
        parallel_file = open(parallel_coords_files, 'w')
        parallel_file.write(simplejson.dumps(par_coords_data))
        parallel_file.close()

        return parallel_coords_files

    def write_summaries(self, aggregated_sets, file_id, items, metrics, time_series, values, window_size,
                        alphabet_size, approximation, mapping=None):

        a = 97
        alphabet = []
        count = 0
        while count < alphabet_size:
            alphabet.append(chr(a + count))
            count += 1

        data_output_representation = {}
        data_output_representation["name"] = file_id
        data_output_representation["sax"] = {"approximation": approximation, "alphabet": alphabet,
                                             "window-size": window_size}
        data_output_representation["time-series"] = values
        data_output_representation["min"] = numpy.min(values)
        data_output_representation["max"] = numpy.max(values)
        data_output_representation["composition"] = items
        # here, iterate through everything and create a top level data structure for the report.
        aggregated_sets = self.add_ngram_to_aggregated_sets(aggregated_sets, metrics, file_id, items, values,
                                                            window_size, mapping)
        # self.generate_paper_slice_metrics(values)
        time_series["time-series"].append(
            {"file": file_id, "min": numpy.min(values), "max": numpy.max(values), "series": values})

        return aggregated_sets, time_series

    def run_analysis(self, analysis_model, output_files=True):

        aggregated_sets = {}
        # calculates metrics for each glyph in each time series
        # "abb": [{"file":"ecg_data_2", "kurtosis":}]
        metrics = {}
        time_series = {"time-series": []}

        alphabetSize = int(analysis_model.alphabet_size)
        window_size = int(analysis_model.window_size)

        processing_times = {}

        swa = NormalizedSequenceAnalysis()

        series_metadata = {}
        total_values = 0
        file_index = 0
        for file in analysis_model.time_series_collection.files.all():
            f = open(file.location, 'r')

            index = 1
            values = []
            values_adv = []
            for line in f:
                split_values = line.split("\t")
                if len(split_values) > 2:
                    clean_string = re.sub('\r\n', '', split_values[2])
                    values.append(float(clean_string))
                    values_adv.append({'x': index, 'y': float(clean_string)})
                else:
                    values.append(float(line))
                    values_adv.append({'x': index, 'y': float(line)})
                index += 1

            total_values += index

            self.sax = saxpy.SAX(eSAX=False, wordSize=len(values) / window_size, alphabetSize=alphabetSize)
            # We want to test the basic example. A time series aggregated.
            (x1String, x1Indices) = self.sax.to_letter_rep(values)

            if analysis_model.algorithm == 'bound_sliding_window':

                start_time = datetime.now()
                swa = SlidingWindowAnalysis()
                items = swa.process_string(x1String, int(analysis_model.algorithm_parameter))

                aggregated_sets, time_series = self.write_summaries(aggregated_sets, file.name, items, metrics,
                                                                    time_series,
                                                                    values, window_size, alphabetSize,
                                                                    x1String)
                # print 'It took ' + str(
                # (datetime.now() - start_time)) + "ms to do that analysis using sliding window with " + str(
                # total_values) + " time points on " + file.name

                processing_times[file.name] = {"time": (datetime.now() - start_time), "point": len(values)}

            elif analysis_model.algorithm == 'max_repeats':

                str1_unicode = unicode(x1String, 'utf-8', 'replace')
                series_metadata[file_index] = {"series": str1_unicode, "name": file.name, "values": values,
                                               "values_adv": values_adv}

            elif analysis_model.algorithm == 'max_repeats_compressed':
                str1_unicode = unicode(x1String, 'utf-8', 'replace')
                compressed_suffix, mapping = swa.process_string(str1_unicode)
                series_metadata[file_index] = {"series": compressed_suffix, "mapping": mapping, "name": file.name,
                                               "values": values,
                                               "values_adv": values_adv}

            file_index += 1
            print 'Just analysed ' + file.name

        if analysis_model.algorithm == 'max_repeats' or analysis_model.algorithm == 'max_repeats_compressed':
            # start_time = datetime.now()
            rstr = Rstr_max()

            for series in series_metadata:
                rstr.add_str(series_metadata[series]["series"])
            r = rstr.go()
            time_series_results = rstr.getFrequentItemsInCollection(r)
            #
            # print 'It took ' + str(
            # (datetime.now() - start_time)) + "ms to do that analysis using maximal repeats with " + str(total_values) + " time points"

            for time_series_result in time_series_results:
                series_metadata_details = series_metadata[time_series_result]

                mapping = None
                if "mapping" in series_metadata_details:
                    mapping = series_metadata_details["mapping"]

                aggregated_sets, time_series = self.write_summaries(aggregated_sets,
                                                                    series_metadata_details["name"],
                                                                    time_series_results[time_series_result],
                                                                    metrics, time_series,
                                                                    series_metadata_details["values"],
                                                                    window_size, alphabetSize,
                                                                    series_metadata_details["series"],
                                                                    mapping)

        count_cut_off = int(analysis_model.cutoff)
        toRemove = []
        for approximation in aggregated_sets:
            if aggregated_sets[approximation]["count"] < count_cut_off:
                toRemove.append(approximation)

        for approximation in toRemove:
            del aggregated_sets[approximation]
        # for item in aggregated_sets:
        # print item

        if output_files:
            linked_graph_file = self.create_linked_graph(aggregated_sets, analysis_model.model_name, window_size)
            analysis_model.network_file = linked_graph_file

            parallel_coords_files = self.create_parallel_coords_plot(aggregated_sets, analysis_model.model_name,
                                                                     window_size)
            analysis_model.parallel_coords_file = parallel_coords_files

            aggregated_ts_file = OUTPUT_DIR + analysis_model.model_name + '_time_series.json'
            ts_file = open(aggregated_ts_file, 'w')
            ts_file.write(simplejson.dumps(time_series))
            ts_file.close()

            analysis_model.time_series_file = aggregated_ts_file
            analysis_model.save()
        else:
            return len(aggregated_sets), total_values