from datetime import datetime
from ChronoGlyph_Web.timeseries_analysis.max_repeats.suffixtree import suffix_tree, tree_to_str, to_lines

__author__ = 'eamonnmaguire'


class NormalizedSequenceAnalysis(object, ):
    def process_string(self, suffix):
        (compressed_suffix, mapping) = self.getCollapsedApproximation(suffix)
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
        count_array = {}

        item_count = 0
        for c in approximation:
            if len(item_array) == 0:
                item_array.append(c)
                count_array[item_count] = 1
            elif c != item_array[item_count]:
                item_array.append(c)
                item_count += 1
                count_array[item_count] = 1
            else:
                count_array[item_count] += 1

        compressed_representation = ""
        for item in item_array:
            compressed_representation += item

        return compressed_representation, count_array

    def extend_approximation_with_mapping(self, position_key, approximation, mapping):
        # mapping tells us for an index in a string, what the actual length was
        actual_approximation = ""
        for c in approximation:
            count = 0
            while count < mapping[position_key]:
                actual_approximation += c
                count += 1

            position_key += 1

        return actual_approximation


if __name__ == '__main__':
    start_time = datetime.now()
    swa = NormalizedSequenceAnalysis()

    compressed_suffix, mapping = swa.process_string("cccccccbbbbbbbbbbbbbbbbbbbbbbbbaaaaabbbbbcccccccccccbb")
    print compressed_suffix
    print mapping
    swa.extend_approximation_with_mapping(2, "ab", mapping)
    print 'It took ' + str((datetime.now() - start_time)) + "ms to do that analysis"
