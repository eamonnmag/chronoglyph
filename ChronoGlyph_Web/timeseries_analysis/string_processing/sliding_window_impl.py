__author__ = 'eamonnmaguire'


class SlidingWindowAnalysis(object):
    def process_string(self, string, window_size):
        index = 0
        summarised_ngrams = {}
        last_item = {"appr": None, "index": -1}
        while index < len(string):
            ngram = string[index:index + window_size]

            if not (ngram in summarised_ngrams):
                summarised_ngrams[ngram] = {}

            if last_item["appr"] != ngram:
                summarised_ngrams[ngram][index] = {"symbolic_approximation": ngram, "repeat_count": 1, "length": len(ngram)}
                last_item["appr"] = ngram
                last_item["index"] = index
            else:
                alt_index = last_item["index"]
                summarised_ngrams[ngram][alt_index]["repeat_count"] += 1
                summarised_ngrams[ngram][alt_index]["length"] += 1


            index += 1

        filtered_output = {}

        for key in summarised_ngrams:

            # we go through the summarised ngrams and determine which should be used for compression
            for potential_ngram_start_index in summarised_ngrams[key]:
                # if summarised_ngrams[key][potential_ngram_start_index]["repeat_count"] > cutoff:
                filtered_output[potential_ngram_start_index] = {
                    "ngram": summarised_ngrams[key][potential_ngram_start_index]}

        return filtered_output


if __name__ == '__main__':
    swa = SlidingWindowAnalysis()
    filtered_output =  swa.process_string("cccccccbbbbbbbbbbbbbbbbbbbbbbbbaaaaabbbbbcccccccccccbb", 5)
    print filtered_output