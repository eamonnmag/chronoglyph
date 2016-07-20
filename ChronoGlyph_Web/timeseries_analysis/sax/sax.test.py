import re
from datetime import datetime
from django.utils import unittest
import numpy
import scipy
import scipy.stats
import simplejson
from ChronoGlyph_Web.timeseries_analysis.max_repeats.rstr_max import Rstr_max
from ChronoGlyph_Web.timeseries_analysis.sax import saxpy


class TestSAX(unittest.TestCase):
    def setUp(self):
        self.sax = saxpy.SAX(eSAX=True)

    def test_compare(self):
        x1 = [0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0]
        x2 = [0, 4.5, 10, 40, -10, 5, 6, 1, 7.6, 0, 9.8, 10, 0]
        x3 = [15, 10, 12, 35, 0, 7, 8, 3, 4, 2, 5, 1, 4]
        x4 = [0, 0, 0, 2, 20, 50, 70, 30, 20, 10, 10, 0, -40]

        # window size of 2 should lead to 12 strings representing each tuple.

        (x1String, x1Indices) = self.sax.to_letter_rep(x1)
        (x2String, x2Indices) = self.sax.to_letter_rep(x2)
        (x3String, x3Indices) = self.sax.to_letter_rep(x3)
        (x4String, x4Indices) = self.sax.to_letter_rep(x4)

        print 'x1String String is: ' + x1String
        print 'x2String String is: ' + x2String
        print 'x3String String is: ' + x3String
        print 'x4String String is: ' + x4String

        print 'Difference in x1 and x2 is ' + str(self.sax.compare_strings(x1String, x2String))
        print 'Difference in x1 and x3 is ' + str(self.sax.compare_strings(x1String, x3String))
        print 'Difference in x2 and x3 is ' + str(self.sax.compare_strings(x2String, x3String))
        print 'Difference in x1 and x4 is ' + str(self.sax.compare_strings(x1String, x4String))
        print 'Difference in x4 and x1 is ' + str(self.sax.compare_strings(x4String, x1String))
        print 'Difference in x2 and x4 is ' + str(self.sax.compare_strings(x2String, x4String))
        print 'Difference in x4 and x3 is ' + str(self.sax.compare_strings(x4String, x3String))

        self.assertEqual(self.sax.compare_strings(x1String, x2String), 0)

    def test_compare_varying_windows(self):
        # depending on window size and alphabet, the SAX representation received will
        # be more or less granular. Here we test the difference.
        x1 = [0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0]
        x2 = [0, 0, 0, 2, 20, 50, 70, 30, 20, 10, 10, 0, -40]
        # x2 = [0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0]

        alphabet = 3
        while alphabet <= 20:

            wordSize = 3

            while wordSize <= 10:
                sax = saxpy.SAX(eSAX=True, alphabetSize=alphabet, wordSize=wordSize)

                print 'Testing with alphabet at ' + str(alphabet) + ' and word size ' + str(wordSize)
                (x1String, x1Indices) = sax.to_letter_rep(x1)
                (x2String, x2Indices) = sax.to_letter_rep(x2)

                print 'x1String String is: ' + x1String
                print 'x2String String is: ' + x2String

                print '\n'

                wordSize += 1
            alphabet += 1

    def test_number_order(self):
        frame = [100, 10, 4.5, -100]
        approximation = []
        self.sax.to_PAA_eSAX_extension(frame, approximation)
        print str(approximation) + '\n'

        self.assertEqual(approximation[0], 100)
        self.assertEqual(approximation[2], -100)

        # Checks simple case where min occurs before max value
        frame = [-100, 10, 100]
        approximation = []
        self.sax.to_PAA_eSAX_extension(frame, approximation)
        print str(approximation) + '\n'

        self.assertEqual(approximation[0], -100)
        self.assertEqual(approximation[2], 100)

        #Checks case where mean occurs before min value
        frame = [10, 40, 40, -10, 10, 50]
        approximation = []
        self.sax.to_PAA_eSAX_extension(frame, approximation)
        print str(approximation) + '\n'

        self.assertEqual(approximation[1], -10)
        self.assertEqual(approximation[2], 50)


    @staticmethod
    def test_stream_find_matches():
        # create random data, although we can't validate on random.
        stream = [0, 1, 35, 2, 32, 10, 20, 402, 1]


    @staticmethod
    def test_find_matches_in_dictionary():
        # create random data, although we can't validate on random.
        dict = []
        values = [0, 1, 35, 2, 32, 10, 20, 402, 1]

    def test_average_case(self):
        print 'Testing SAX - Window size = 2, alphabet = 4'
        x1 = [0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0,
              10.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0, 5.5, 10, 57, -10, 5, 6, 1, 9.6, -2, 9.8, 14, 0]

        self.sax = saxpy.SAX(eSAX=False, wordSize=len(x1), alphabetSize=4)
        # We want to test the basic example. A time series aggregated.
        (x1String, x1Indices) = self.sax.to_letter_rep(x1)

        print 'x1String String is: ' + x1String

        # tree = suffix_tree(x1String)
        #print tree_to_str(tree)

        rstr = Rstr_max()
        str1 = x1String
        str1_unicode = unicode(str1, 'utf-8', 'replace')
        rstr.add_str(str1_unicode)

        r = rstr.go()

        rstr.outputResult(r)
        self.assertFalse(False)


    def add_ngram_to_aggregated_sets(self, aggregated_sets, metrics, file, items, time_series, window_size):
        occurrences = {}

        # w_s = minimum space required for distinct visualization of point in time series
        w_s = 2
        # w_g = glyph width in the display - helps us calculate how much space can be saved
        w_g = 40
        for position_key in items:
            ngram = items[position_key]["ngram"]

            approximation = ngram["symbolic_approximation"]
            if len(approximation) > 1:
                if not approximation in aggregated_sets:
                    aggregated_sets[approximation] = {"id": len(aggregated_sets),
                                                      "approximation": approximation,
                                                      "count": 0, "metrics": [], "series": []}
                if not approximation in occurrences:
                    occurrences[approximation] = {}

                aggregated_sets[approximation]["count"] += 1

                if not file["prepender"] in occurrences[approximation]:
                    occurrences[approximation][file["prepender"]] = []

                occurrences[approximation][file["prepender"]].append(
                    [int(position_key) * window_size, (int(position_key) + ngram["length"]) * window_size])

                if not approximation in metrics:
                    metrics[approximation] = []
                    # now calculate the stats for this motif given the context area...

                series_slice = time_series[
                               int(position_key) * window_size: (int(position_key) + ngram["length"]) * window_size]
                metrics[approximation].append(
                    {
                        "Kurtosis": scipy.stats.kurtosis(series_slice, fisher=False, bias=False),
                        # "Kurtosis (Fisher)": scipy.stats.kurtosis(series_slice, fisher=True, bias=False),
                        "Skewedness": scipy.stats.skew(series_slice, bias=False),
                        "Length": len(approximation),
                        "Max": numpy.max(series_slice),
                        "Min": numpy.min(series_slice),
                        "Mean": scipy.stats.nanmean(series_slice),
                        "Median": scipy.stats.nanmedian(series_slice),
                        "Deviation": scipy.stats.nanstd(series_slice),
                        "Std Error": scipy.stats.sem(series_slice),
                        "Pixel Saving Ptnl": (w_s * ngram["length"] * window_size) / w_g,
                        "Compression Ptnl.": (ngram["length"] * window_size * aggregated_sets[approximation]["count"]) /
                                             aggregated_sets[approximation]["count"],
                        #"Burstiness": self.burstiness(series_slice),
                        #"Variance Coefficient": self.variance_coefficient(series_slice),
                        "Volatility": scipy.stats.nanstd(series_slice) / scipy.stats.nanmean(series_slice)})

        for approximation in metrics:
            # aggregate the metrics we have, ignoring nans where they exist scipy.stats.nanmean(values)
            metric_values = {}
            for val in metrics[approximation]:
                for key in val:
                    if not key in metric_values:
                        metric_values[key] = []

                    metric_values[key].append(val[key])

            for metric in metric_values:
                aggregated_sets[approximation]["metrics"].append(
                    {"name": metric, "value": round(scipy.stats.nanmean(metric_values[metric]), 3)})

        for ngram in occurrences:
            aggregated_sets[ngram]["series"].append(
                {"file": file["prepender"], "positions": occurrences[ngram][file["prepender"]]})

    def burstiness(self, series_slice):
        # calculated as in http://www.mitpressjournals.org/doi/pdf/10.1162/089976603322518759
        count = 0
        running_sum = 0
        while count < len(series_slice) - 1:
            running_sum += (3 * scipy.power(series_slice[count] - series_slice[count + 1], 2)) / \
                           scipy.power(series_slice[count] + series_slice[count + 1], 2)
            count += 1

        return (1 / len(series_slice)) * running_sum


    def generate_paper_slice_metrics(self, values):
        # ADDITIONAL SLICES for paper stats
        slices = {"slice1": {"data": values[938:1876], "results": {}},
                  "slice2": {"data": values[3001:3939], "results": {}},
                  "slice3": {"data": values[2970:4018], "results": {}},
                  "slice4": {"data": values[3969:4907], "results": {}},
                  "slice5": {"data": values[9969:10907], "results": {}},
                  "slice6": {"data": values[12953:13891], "results": {}}}

        for slice in slices:
            slice_data = slices[slice]["data"]
            slices[slice]["results"] = {
                "Kurtosis": scipy.stats.kurtosis(slice_data, fisher=False, bias=False),
                "Skewness": scipy.stats.skew(slice_data, bias=False),
                "Max": numpy.max(slice_data),
                "Min": numpy.min(slice_data),
                "Mean": scipy.stats.nanmean(slice_data),
                "Median": scipy.stats.nanmedian(slice_data),
                "Deviation": scipy.stats.nanstd(slice_data),
                "Std Error": scipy.stats.sem(slice_data),
                "Volatility": scipy.stats.nanstd(slice_data) / scipy.stats.nanmean(slice_data)}

            slices[slice]["data"] = []

            print slice
            print slices[slice]

    def testCaseOnLargeFiles(self):

        # files = [{"name": "ECG Data 1", "prepender": "ecg_data_1",
        # "file": "../datasets/ECG_data/chfdb_chf01_275.txt"},
        #          {"name": "ECG Data 2", "prepender": "ecg_data_2",
        #           "file": "../datasets/ECG_data/chfdb_chf13_45590.txt"},
        #          {"name": "ECG Data 3", "prepender": "ecg_data_3",
        #           "file": "../datasets/ECG_data/ltstdb_20221_43.txt"},
        #          {"name": "ECG Data 4", "prepender": "ecg_data_4",
        #           "file": "../datasets/ECG_data/ltstdb_20321_240.txt"},
        #          {"name": "ECG Data 5", "prepender": "ecg_data_5",
        #           "file": "../datasets/ECG_data/mitdb__100_180.txt"},
        #          {"name": "ECG Data 6", "prepender": "ecg_data_6",
        #           "file": "../datasets/ECG_data/stdb_308_0.txt"},
        #          {"name": "ECG Data 7", "prepender": "ecg_data_7",
        #           "file": "../datasets/ECG_data/xmitdb_x108_0.txt"},
        # ]

        files = [{"name": "Efficiency", "prepender": "efficiency_1",
                  "file": "/Users/eamonnmaguire/Downloads/efficiency.csv"}]

        #files = [{"name": "Space_Shuttle", "prepender": "shuttle_1",
        #          "file": "../../datasets/Space_Shuttle/TEK17.txt"},
        #         {"name": "Space_Shuttle", "prepender": "shuttle_2",
        #          "file": "../../datasets/Space_Shuttle/TEK16.txt"},
        #         {"name": "Space_Shuttle", "prepender": "shuttle_3",
        #          "file": "../../datasets/Space_Shuttle/TEK14.txt"}]


        # we need to create a summary document arranging the glyphs by their approximation and
        # window size - can just do approximation for now...
        # stores in the format "abb":{
        #                           "id":0,
        #                           "approximation":"abb",
        #                           "count":100,
        #                           "series":[
        #                               {"file":"ecg_data_2",
        #                                "positions":
        #                                   [[0,4],[7,10]]}],
        #                           "metrics":[
        #                               {"kurtosis":0.32}
        #                           }
        aggregated_sets = {}
        # calculates metrics for each glyph in each time series
        # "abb": [{"file":"ecg_data_2", "kurtosis":}]
        metrics = {}
        time_series = {"time-series": []}

        for file in files:
            f = open(file["file"], 'r')

            index = 1
            values = []
            values_adv = []
            for line in f:
                split_values = line.split(",")
                if len(split_values) > 1:
                    clean_string = re.sub('\r\n', '', split_values[1])
                    values.append(float(clean_string))
                    values_adv.append({'x': index, 'y': float(clean_string)})
                else:
                    values.append(float(line))
                    values_adv.append({'x': index, 'y': float(line)})
                index += 1

            window_size = 200

            print 'There are ' + str(len(values)) + " values in this series."

            self.sax = saxpy.SAX(eSAX=False, wordSize=len(values) / window_size, alphabetSize=6)
            # We want to test the basic example. A time series aggregated.
            start_time = datetime.now()

            (x1String, x1Indices) = self.sax.to_letter_rep(values)

            total_time = (datetime.now() - start_time)
            total_milliseconds = int(total_time.total_seconds() * 1000)

            print 'Analysing with (w=' + str(window_size) + ', a=' + str(6) + ') took ' + str(
                total_milliseconds) + ' ms'

            print 'Approximation size is ' + str(len(x1String))
            print x1String

            out_file = open("timeseries-obj.json", 'w+')

            obj = {"time-series": [{"series": values, "max": 1, "min": -1, "file": 'test.txt'}]}
            out_file.write(simplejson.dumps(obj))
            out_file.close()

            #tree = suffix_tree(x1String)
            #print tree_to_str(tree)

            rstr = Rstr_max()
            str1 = x1String
            str1_unicode = unicode(str1, 'utf-8', 'replace')
            rstr.add_str(str1_unicode)

            r = rstr.go()

            #rstr.outputResult(r)
            items = rstr.getFrequentItemsInCollection(r)

            data_output_representation = {}
            data_output_representation["name"] = file["name"]
            data_output_representation["sax"] = {"approximation": x1String, "alphabet": ['a', 'b', 'c'],
                                                 "window-size": window_size}
            data_output_representation["time-series"] = values
            data_output_representation["min"] = numpy.min(values)
            data_output_representation["max"] = numpy.max(values)
            data_output_representation["composition"] = items

            # here, iterate through everything and create a top level data structure for the report.

            self.add_ngram_to_aggregated_sets(aggregated_sets, metrics, file, items, values, window_size)

            #self.generate_paper_slice_metrics(values)

            time_series["time-series"].append(
                {"file": file["prepender"], "min": numpy.min(values), "max": numpy.max(values), "series": values})

            # write main file
            summary_file = open(
                '../datasets/outputs/' + file["prepender"] + '_summary_w' + str(window_size) + '.json',
                'w')
            summary_file.write(simplejson.dumps(data_output_representation))
            summary_file.close()

            data_output_representation = {"Name": file["name"], "data": values_adv}
            # write additional file required for rickshaft.
            summary_file = open('../datasets/outputs/' + file["prepender"] + '_summary_rickshaft.json', 'w')
            summary_file.write(simplejson.dumps(data_output_representation))
            summary_file.close()

        aggregated_sets_file = open('../datasets/outputs/aggregate_' + str(window_size) + '.json', 'w')
        aggregated_sets_file.write(simplejson.dumps(aggregated_sets))
        aggregated_sets_file.close()

        count_cut_off = 0

        unlinked_graph = {"nodes": [], "links": []}
        for approximation in aggregated_sets:
            if aggregated_sets[approximation]["count"] > count_cut_off:
                unlinked_graph["nodes"].append(aggregated_sets[approximation])

        graph_file = open(
            '../datasets/outputs/' + file["prepender"] + '_unlinked_graph_' + str(window_size) + '.json', 'w')
        graph_file.write(simplejson.dumps(unlinked_graph))
        graph_file.close()

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
                    if aggregated_sets[approximation]["count"] > count_cut_off and aggregated_sets[approximation2][
                        "count"] > count_cut_off:
                        distance = self.sax.compare_strings(approximation, approximation2) * 100
                        distance_graph["links"].append({"id": count, "source": aggregated_sets[approximation]["id"],
                                                        "target": aggregated_sets[approximation2]["id"],
                                                        "value": distance})
                        seen.append(key_1)
                        count += 1

        graph_file = open(
            '../datasets/outputs/' + file["prepender"] + '_distance_graph_' + str(window_size) + '.json', 'w')
        graph_file.write(simplejson.dumps(distance_graph))
        graph_file.close()

        graph_file = open('../datasets/outputs/' + file["prepender"] + '_par_coords_' + str(window_size) + '.json',
                          'w')

        par_coords_data = []
        for approximation in aggregated_sets:
            if aggregated_sets[approximation]["count"] > count_cut_off:
                record = {"id": aggregated_sets[approximation]["id"],
                          "Approximation": approximation,
                          "Frequency": aggregated_sets[approximation]["count"]}

                for metric in aggregated_sets[approximation]["metrics"]:
                    record[metric["name"]] = metric["value"]

                par_coords_data.append(record)

        graph_file.write(simplejson.dumps(par_coords_data))
        graph_file.close()

        ts_file = open(
            '../datasets/outputs/' + file["prepender"] + '_time_series.json',
            'w')
        ts_file.write(simplejson.dumps(time_series))
        ts_file.close()


if __name__ == '__main__':
    unittest.main()