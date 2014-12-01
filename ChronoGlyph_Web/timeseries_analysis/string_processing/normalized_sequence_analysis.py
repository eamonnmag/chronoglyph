from datetime import datetime
from ChronoGlyph_Web.timeseries_analysis.max_repeats.suffixtree import suffix_tree, tree_to_str, to_lines

__author__ = 'eamonnmaguire'


class NormalizedSequenceAnalysis(object, ):
    def process_string(self, suffix):
        (compressed_suffix, count_mapping, compressed_count_mapping) = self.getCollapsedApproximation(suffix)
        mapping = {"count_mapping": count_mapping, "compressed_count_mapping": compressed_count_mapping}

        return compressed_suffix, mapping


    def getCollapsedApproximation(self, approximation):
        """
        Collapses an approximation, say aaaabbcc in to aabc.
        Short sequences, with say 1-3 repeats are represented as one letter
        Medium sequences, with say 4-7 repeats are represented as 3 letters
        Long sequences, with say 7+ repeats are represented as 5 letter
        This helps circumvent problems with similar sequences that have slightly different repeats.
        It's not perfect, but it's better.
        :param approximation: aaaabbcc
        :return: aabc
        """

        item_array = []
        item_count = {}
        compressed_count_mapping = {}
        full_count_mapping = {}

        count = 0
        for c in approximation:
            if len(item_array) == 0:
                item_array.append(c)
                item_count[count] = 1
            elif c != item_array[count]:
                item_array.append(c)
                count += 1
                item_count[count] = 1
            else:
                item_count[count] += 1

        running_count = 0
        compressed_representation = ""
        for count in item_count:
            full_count_mapping[running_count] = item_count[count]
            if item_count[count] <= 3:
                compressed_count_mapping[running_count] = 1
            elif item_count[count] <= 6:
                compressed_count_mapping[running_count] = 2
            else:
                compressed_count_mapping[running_count] = 3

            compressed_representation += item_array[count] + str(compressed_count_mapping[running_count])
            running_count += 2

        return compressed_representation, full_count_mapping, compressed_count_mapping


    def extend_approximation(self, position_key, approximation, mapping):
        # mapping tells us for an index in a string, what the actual length was
        actual_approximation = ""
        for c in approximation:
            count = 0
            if not c.isdigit():
                while count < mapping[position_key]:
                    actual_approximation += c
                    count += 1

            position_key += 1

        return actual_approximation


    def expand_numeric_approximation(self, position_key, approximation, compressed_count_mapping):
        # mapping tells us for an index in a string, what the actual length was
        actual_approximation = ""
        for c in approximation:
            count = 0
            if not c.isdigit():
                while count < compressed_count_mapping[position_key]:
                    actual_approximation += c
                    count += 1

            position_key += 1

        return actual_approximation


if __name__ == '__main__':
    start_time = datetime.now()
    swa = NormalizedSequenceAnalysis()

    (compressed_suffix, mapping) \
        = swa.process_string("cccccccbbbbbbbbbbbbbbbbbbbbbbbbaaaaabbbbbcccccccccccbb")
    print compressed_suffix
    print mapping["count_mapping"]
    print mapping["compressed_count_mapping"]
    print swa.extend_approximation(0, "c2b3a2b2", mapping["count_mapping"])
    print swa.expand_numeric_approximation(0, "c2b3a2b2", mapping["compressed_count_mapping"])
    print 'It took ' + str((datetime.now() - start_time)) + "ms to do that analysis"
