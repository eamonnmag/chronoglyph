__author__ = 'eamonnmaguire'


class Ngram(object):
    def __init__(self, representation):
        self.representation = representation
        self.occurrence_count = 1
        self.timeseries_appears_in = []
        self.score = 0

    def calculate_compression_potential(self):
        return self.occurrence_count * len(self.representation)

    def __unicode__(self):
        return self.representation + "\t" + str(self.occurrence_count) + "\t" + str(
            len(self.timeseries_appears_in)) + "\t" + str(self.score)