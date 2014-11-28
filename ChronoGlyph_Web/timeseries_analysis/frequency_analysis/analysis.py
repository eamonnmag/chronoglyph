import math
import numpy
from ts_approximation.frequency_analysis.ngram import Ngram
from ts_approximation.max_repeats.rstr_max import Rstr_max
from ts_approximation.sax import saxpy

__author__ = 'eamonnmaguire'


class FrequencyAnalysis(object):
    def __init__(self):
        self.ngrams = {}


    def encodeAsUtf8(self, str):
        str1_unicode = unicode(str, 'utf-8', 'replace')
        return str1_unicode

    def analyse_all_series(self, time_series_list):
        sax_representations = []

        for series in time_series_list:
            sax_representations.append(self.analyse_series(series))

        print str(sax_representations)
        rstr = Rstr_max()

        for sax_representation in sax_representations:
            str1_unicode = self.encodeAsUtf8(sax_representation)
            rstr.add_str(str1_unicode)

        r = rstr.go()
        filtered_ngrams = self.getFrequentItems(rstr, r)

        return

    def analyse_series(self, time_series):

        window_size = 1
        print 'There are ' + str(len(time_series)) + " values in this series."

        self.sax = saxpy.SAX(eSAX=False, wordSize=len(time_series) / window_size, alphabetSize=6)
        # We want to test the basic example. A time series aggregated.
        (x1String, x1Indices) = self.sax.to_letter_rep(time_series)

        return x1String


    def getFrequentItems(self, rstr, r):
        result = {}

        occurrences = []
        time_series_occurrences = []

        for (offset_end, occurrence_count), (l, start_plage) in r.iteritems():
            ss = rstr.global_suffix[offset_end - l:offset_end]

            if len(ss) > 0:
                if not ss.encode('utf-8') in result.keys():
                    result[ss.encode('utf-8')] = Ngram(ss.encode('utf-8'))

                for o in range(start_plage, start_plage + occurrence_count):
                    offset_global = rstr.res[o]
                    id_str = rstr.idxString[offset_global]

                    if not id_str in result[ss.encode('utf-8')].timeseries_appears_in:
                        result[ss.encode('utf-8')].timeseries_appears_in.append(id_str)

                    result[ss.encode('utf-8')].occurrence_count += 1

                occurrences.append(result[ss.encode('utf-8')].occurrence_count)
                time_series_occurrences.append(len(result[ss.encode('utf-8')].timeseries_appears_in))

        max = numpy.max(occurrences)
        max_ts = numpy.max(time_series_occurrences)

        high_scoring_ngrams = {}
        f = open('../../datasets/outputs/ngrams.txt', 'w')
        for ngram in result:
            # we should calculate a score here. similar to automacron
            # score equals occurrence/max + time_series_count/total series
            result[ngram].score = float(result[ngram].occurrence_count) / max + float(
                len(result[ngram].timeseries_appears_in)) / max_ts
            if result[ngram].score > 1:
                high_scoring_ngrams[result[ngram].representation] = result[ngram]
                f.write(result[ngram].__unicode__() + "\n")

        f.close()
        return high_scoring_ngrams


    def filter_ngrams(self, rstr, r, filter):
        result = {}

        for (offset_end, occurrence_count), (l, start_plage) in r.iteritems():
            ss = rstr.global_suffix[offset_end - l:offset_end]

            # at this point, we want to compress every thing down using the composition rules we have.
            # This requires a sorting on the key so that we know that everything is in order.

            if ss.encode('utf-8') in filter.keys():
                result[ss.encode('utf-8')] = []
                for o in range(start_plage, start_plage + occurrence_count):
                    offset_global = rstr.res[o]
                    offset = rstr.idxPos[offset_global]
                    result[ss.encode('utf-8')].append(offset)

        # now process this array: sort the offsets, and determine what items are side by side. We create an
        # ngram for each which we'll filter afterwards
        summarised_ngrams = {}
        for key in result.keys():
            sorted = numpy.sort(result[key])

            if not key in summarised_ngrams.keys():
                summarised_ngrams[key] = {}

            last_stored_start_index = -1
            count = 1
            iteration_count = 0
            for value in sorted:

                if last_stored_start_index == -1:
                    summarised_ngrams[key][str(value)] = {"length": len(key), "symbolic_approximation": key,
                                                          "repeat_count": 1}
                    last_stored_start_index = str(value)
                elif int((value - (count * len(key)))) == int(last_stored_start_index):
                    summarised_ngrams[key][last_stored_start_index]["length"] += len(key)
                    summarised_ngrams[key][last_stored_start_index]["repeat_count"] += 1
                    count += 1
                elif value == sorted[iteration_count - 1] + 1:
                    # we have a chain, like so
                    # todo: check the distance here...
                    #1718 {'repeat_count': 1, 'length': 14, 'symbolic_approximation': 'aaaaaaaaaaaaaa'}
                    #1719 {'repeat_count': 1, 'length': 14, 'symbolic_approximation': 'aaaaaaaaaaaaaa'}
                    #1720 {'repeat_count': 1, 'length': 14, 'symbolic_approximation': 'aaaaaaaaaaaaaa'}
                    summarised_ngrams[key][last_stored_start_index]["length"] += 1
                    count += 1
                else:
                    #reset count since we are now looking for another pattern
                    summarised_ngrams[key][str(value)] = {"length": len(key), "symbolic_approximation": key,
                                                          "repeat_count": 1}
                    last_stored_start_index = str(value)
                    count = 1

                iteration_count += 1

        return summarised_ngrams


    def splitTimeSeries(self, time_series, number_of_splits, output_dir, file_prepender):
        section_lengths = len(time_series) / number_of_splits

        count = 0
        while count < number_of_splits:
            outfile = open((output_dir + file_prepender + "_" + str((count + 1)) + ".txt"), 'w')
            if count == number_of_splits - 1:
                #output the rest of the array
                outfile.writelines(list("%s\n" % str(item) for item in time_series[count * section_lengths:]))
            else:
                #output the section
                outfile.writelines(list(
                    "%s\n" % str(item) for item in time_series[count * section_lengths:(count + 1) * section_lengths]))
            outfile.close()
            count += 1


class AnalysisTest:
    def __init__(self):
        print "started test"

    def run(self):
        files = [{"name": "Patient_1_1", "prepender": "ecg_1", "file": "../../datasets/ECG_data/chfdb_chf01_275.txt"},
                 {"name": "Patient_1_2", "prepender": "ecg_2", "file": "../../datasets/ECG_data/chfdb_chf13_45590.txt"},
                 {"name": "Patient_1_3", "prepender": "ecg_3", "file": "../../datasets/ECG_data/ltstdb_20221_43.txt"},
                 {"name": "Patient_1_4", "prepender": "ecg_4", "file": "../../datasets/ECG_data/ltstdb_20321_240.txt"},
                 {"name": "Patient_1_5", "prepender": "ecg_5", "file": "../../datasets/ECG_data/mitdb__100_180.txt"},
                 {"name": "Patient_1_6", "prepender": "ecg_6", "file": "../../datasets/ECG_data/stdb_308_0.txt"},
                 {"name": "Patient_1_7", "prepender": "ecg_7", "file": "../../datasets/ECG_data/xmitdb_x108_0.txt"},
        ]

        freq_analysis = FrequencyAnalysis()
        all_time_series = []
        for file in files:
            f = open(file["file"], 'r')
            time_series = []
            for line in f:
                time_series.append(float(line.split("\t")[2].strip()))

            freq_analysis.splitTimeSeries(time_series, 3, '../../outputs/splits/', file['name'] + "_split")
            all_time_series.append(time_series)

        freq_analysis = FrequencyAnalysis()
        filtered_items = freq_analysis.analyse_all_series(all_time_series)


if __name__ == "__main__":
    AnalysisTest().run()
