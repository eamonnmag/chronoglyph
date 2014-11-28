#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
from collections import OrderedDict
import numpy
from ChronoGlyph_Web.timeseries_analysis.max_repeats.tools_karkkainen_sanders import direct_kark_sort


class Rstr_max:
    def __init__(self):
        self.array_str = []

    def add_str(self, str_unicode):
        self.array_str.append(str_unicode)

    def get_str(self):
        return self.array_str

    def step1_sort_suffix(self):
        char_frontier = chr(2)

        self.global_suffix = char_frontier.join(self.array_str)

        nbChars = len(self.global_suffix)
        init = [-1] * nbChars
        self.idxString = array('i', init)
        self.idxPos = array('i', init)
        self.endAt = array('i', init)

        k = idx = 0
        for mot in self.array_str:
            last = k + len(mot)
            for p in xrange(len(mot)):
                self.idxString[k] = idx
                self.idxPos[k] = p
                self.endAt[k] = last
                k += 1
            idx += 1
            k += 1

        # print 'Global suffix is ' + str(self.global_suffix)
        # print 'idxString is ' + str(self.idxString)
        # print 'idxPos is ' + str(self.idxPos)
        # print 'idxEndAt is ' + str(self.endAt)

        self.res = direct_kark_sort(self.global_suffix)

        # print 'sorted is ' + str(self.res)

    def step2_lcp(self):
        n = len(self.res)
        init = [0] * n
        rank = array('i', init)
        LCP = array('i', init)

        s = self.global_suffix
        suffix_array = self.res
        endAt = self.endAt

        for i in xrange(len(self.array_str), n):
            v = self.res[i]
            rank[v] = i

        l = 0
        for j in xrange(n):
            if (l > 0):
                l -= 1
            i = rank[j]
            j2 = suffix_array[i - 1]
            if i:
                while l + j < endAt[j] and l + j2 < endAt[j2] and s[j + l] == s[j2 + l]:
                    l += 1
                LCP[i - 1] = l
            else:
                l = 0
        self.lcp = LCP

        # print 'LCP is ' + str(self.lcp)


    def step3_rstr(self):
        prev_len = 0
        idx = 0
        results = {}
        len_lcp = len(self.lcp) - 1

        # lcp = self.lcp
        # res = self.res

        class Stack:
            pass

        stack = Stack()
        stack._top = 0
        stack.lst_max = []

        if len(self.res) == 0:
            return {}

        pos1 = self.res[0]
        # offset1 = self.idxPos[self.res[0]]
        # idStr1 = self.idxString[self.res[0]]
        for idx in xrange(len_lcp):
            current_len = self.lcp[idx]
            pos2 = self.res[idx + 1]
            # offset2 = self.idxPos[pos2]
            # idStr2 = self.idxString[pos2]
            # offset2, idStr2  = self.array_suffix[idx+1]
            end_ = max(pos1, pos2) + current_len  # max(pos1, pos2) + current_len
            # e = max((idStr1, offset1), (idStr2, offset2))
            # end_ = (e[0],e[1]+current_len)
            n = prev_len - current_len
            if n < 0:
                #pushMany
                stack.lst_max.append([-n, idx, end_])
                stack._top += -n
            elif n > 0:
                self.removeMany(stack, results, n, idx)
            elif stack._top > 0 and end_ > stack.lst_max[-1][-1]:
                #setMax
                stack.lst_max[-1][-1] = end_

            prev_len = current_len
            pos1 = pos2
            #offset1 = offset2
            #idStr1 = idStr2

        if (stack._top > 0):
            self.removeMany(stack, results, stack._top, idx + 1)

        # print 'Results ' + str(results)
        return results

    def removeMany(self, stack, results, m, idxEnd):
        prevStart = -1
        while m > 0:
            n, idxStart, maxEnd = stack.lst_max.pop()
            if prevStart != idxStart:
                # idStr = self.idxString[maxEnd-1]
                # pos = self.idxPos[maxEnd-1]
                id_ = (maxEnd, idxEnd - idxStart + 1)
                if id_ not in results or results[id_][0] < stack._top:
                    results[id_] = (stack._top, idxStart)
                prevStart = idxStart
            m -= n
            stack._top -= n
        if m < 0:
            stack.lst_max.append([-m, idxStart, maxEnd - n - m])
            stack._top -= m

    def go(self):
        # import time
        # t_start = t0 = time.time()
        # t0 = time.time()
        self.step1_sort_suffix()
        # print time.time() - t0
        # t0 = time.time()
        self.step2_lcp()
        # print time.time() - t0
        # t0 = time.time()
        r = self.step3_rstr()
        # print time.time() - t0
        # print time.time() - t_start
        return r

    def outputResult(self, r):


        for (offset_end, nb), (l, start_plage) in r.iteritems():
            ss = self.global_suffix[offset_end - l:offset_end]
            id_chaine = self.idxString[offset_end - 1]
            s = self.array_str[id_chaine]
            print '[%s] %d' % (ss.encode('utf-8'), nb)
            for o in range(start_plage, start_plage + nb):
                offset_global = self.res[o]
                offset = self.idxPos[offset_global]
                id_str = self.idxString[offset_global]
                print '   (%i, %i)' % (offset, id_str)

                sss = self.global_suffix[offset_global:offset_global + l]
                print '   ', sss

                sss = self.array_str[id_str][offset:offset + l]
                print '   ', sss


    def calculateCutoff(self, r):
        # we want to calculate which items will give the best compression without there being too many glyphs. So
        # occurrences should be limited to 10, unless the representations are all right beside each, in which case,
        # it should be joined as one

        for (offset_end, occurrence_count), (l, start_plage) in r.iteritems():
            ss = self.global_suffix[offset_end - l:offset_end]


    def getFrequentItemsInCollection(self, r):
        """
        While the original algorithm only considers one sequence at a time, this algorithm looks at all sequences
        and finds the matches in one step
        :param r: r_str_max object
        :param series: array of time series approximations being analysed. These should be in order of their addition to the algorithm.
        :return: dictionary
        """
        summarised_ngrams = {}
        series_count = {}
        last_stored_start_index = {}

        for (offset_end, occurrence_count), (l, start_plage) in r.iteritems():
            ss = self.global_suffix[offset_end - l:offset_end]

            if len(ss) > 1:
            # at this point, we want to compress every thing down using the composition rules we have.
            # This requires a sorting on the key so that we know that everything is in order.
                result = {}
                result[ss.encode('utf-8')] = []
                for o in range(start_plage, start_plage + occurrence_count):
                    offset_global = self.res[o]
                    offset = self.idxPos[offset_global]
                    result[ss.encode('utf-8')].append({"offset": offset, "id_str": self.idxString[offset_global]})

                for key in result.keys():
                    for offset_info in result[key]:
                        approximation_id = offset_info["id_str"]
                        offset_value = offset_info["offset"]

                        if not (approximation_id in series_count):
                            series_count[approximation_id] = 0
                            last_stored_start_index[approximation_id] = -1

                        if not (approximation_id in summarised_ngrams):
                            summarised_ngrams[approximation_id] = {}

                        if not (key in summarised_ngrams[approximation_id]):
                            summarised_ngrams[approximation_id][key] = {}

                        last_stored_index = last_stored_start_index[approximation_id]

                        if last_stored_index == -1:
                            summarised_ngrams[approximation_id][key][offset_value] = {"length": len(key),
                                                                                      "symbolic_approximation": key,
                                                                                      "repeat_count": 1}
                            last_stored_start_index[approximation_id] = offset_value

                        elif int((offset_value - (series_count[approximation_id] * len(key)))) == int(
                                last_stored_index):
                            summarised_ngrams[approximation_id][key][last_stored_index]["length"] += len(key)
                            summarised_ngrams[approximation_id][key][last_stored_index]["repeat_count"] += 1
                        else:
                            # reset count since we are now looking for another pattern
                            summarised_ngrams[approximation_id][key][offset_value] = {"length": len(key),
                                                                                      "symbolic_approximation": key,
                                                                                      "repeat_count": 1}
                            last_stored_start_index[approximation_id] = offset_value

                        series_count[approximation_id] += 1

        filtered_output = {}

        for series_id in summarised_ngrams:

            if not (series_id in filtered_output):
                filtered_output[series_id] = {}

            # we go through the summarised ngrams and determine which should be used for compression
            for approximation_key in summarised_ngrams[series_id]:
                for start_index in summarised_ngrams[series_id][approximation_key]:
                    # if summarised_ngrams[key][potential_ngram_start_index]["repeat_count"] > cutoff:
                    filtered_output[series_id][start_index] = {
                        "ngram": summarised_ngrams[series_id][approximation_key][start_index]}

        return filtered_output


if (__name__ == '__main__'):
    str1 = 'toto'
    str1_unicode = unicode(str1, 'utf-8', 'replace')
    rstr = Rstr_max()
    rstr.add_str(str1_unicode)
    rstr.add_str(str1_unicode)
    r = rstr.go()

    print str(r)
    print
    print 'idxstring = ' + str(rstr.idxString)

    for ((id_str, end), nb), (l, start_plage) in r.iteritems():
        ss = rstr.array_str[id_str][end - l:end]
        print '[%s] %d' % (ss.encode('utf-8'), nb)
