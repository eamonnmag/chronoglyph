from ChronoGlyph_Web.timeseries_analysis.max_repeats.suffixtree import suffix_tree, tree_to_str, to_lines

__author__ = 'eamonnmaguire'

class SuffixAnalysis(object, ):

    def process_string(self, suffix):
        tree = suffix_tree(suffix)
        print tree_to_str(tree)
        print to_lines(tree, tree.root)

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

        for count in count_array:
            if count_array[count] <= 3:
                count_array[count] = 1
            elif count_array[count] <= 6:
                count_array[count] = 2
            else:
                count_array[count] = 3

        count = 0
        compressed_representation = ""
        for item in item_array:
            inner_count = 0
            while inner_count < count_array[count]:
                compressed_representation += item
                inner_count += 1
            count += 1

        return compressed_representation


if __name__ == '__main__':
    swa = SuffixAnalysis()
    swa.process_string("cccccccbbbbbbbbbbbbbbbbbbbbbbbbaaaaabbbbbcccccccccccbb")
