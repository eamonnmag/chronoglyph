#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ChronoGlyph_Web.timeseries_analysis.max_repeats.rstr_max import Rstr_max


rstr = Rstr_max()
str1 = 'aacccccbbbbbbbbbbbbbbbbbbbbbbbbaaaaabbbbbcccccccccccbb'
str2 = 'caaccccbabbbbbbbbbbbbbbaaaabbbbaaaaabbbbbcccccccccccbb'
str3 = 'caaccccbabbbbbbbbbbbbbbaaaabbbbaaaaabbbbbcccccccccccbb'
# str1 = 'a'*100000
str1_unicode = unicode(str1, 'utf-8', 'replace')
str2_unicode = unicode(str2, 'utf-8', 'replace')
str3_unicode = unicode(str3, 'utf-8', 'replace')
rstr.add_str(str1_unicode)
rstr.add_str(str2_unicode)
rstr.add_str(str3_unicode)

r = rstr.go()

for (offset_end, nb), (l, start_plage) in r.iteritems():
    ss = rstr.global_suffix[offset_end - l:offset_end]
    id_chaine = rstr.idxString[offset_end - 1]
    s = rstr.array_str[id_chaine]
    print '[%s] %d' % (ss.encode('utf-8'), nb)
    for o in range(start_plage, start_plage + nb):
        offset_global = rstr.res[o]
        offset = rstr.idxPos[offset_global]
        id_str = rstr.idxString[offset_global]
        print '   (%i, %i)' % (offset, id_str)

        sss = rstr.global_suffix[offset_global:offset_global + l]
        print '   ', sss

        sss = rstr.array_str[id_str][offset:offset + l]
        print '   ', sss
