import math
from numpy import arange, array, ones, linalg

from django.utils import unittest
from ChronoGlyph_Web.timeseries_analysis.utils import createBands, mapToBandedArea, normalize, \
    DifferentSizedArrayException

__author__ = 'eamonnmaguire'

import numpy as np

class TestApproximation(unittest.TestCase):
    f = open('distribution-outputs-normalised.txt', 'w')

    def setUp(self):
        self.y_vals = [23, 8, 0, 9, 78, 21, 67, 36, 53, 33, 2, 7, 4, 44, 33, 22, 65, 80, 74, 75]
        self.y_vals = normalize(self.y_vals, 1e-6)

    def testSimpleAverageCase(self):
        #S1:avg
        print 'Testing for S1:avg'

        delta, deltaHalfpoint = createBands(np.min(self.y_vals), np.max(self.y_vals), 16)

        value = mapToBandedArea(np.mean(self.y_vals), 0, delta, deltaHalfpoint)

        print "S1:avg=", str(value)

        modified_array = np.empty(20)
        modified_array.fill(value)

        self.f.write('S1:avg\n')
        self.f.write('Average = ' + str(value) + '\n')
        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)
        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)

        self.f.write('\n')

        print ''


    def testSimpleAverageCase2Windows(self):
        # S2:avg2
        print 'Testing for S2:avg2'
        self.f.write('S2:avg2\n')
        
        delta, deltaHalfpoint = createBands(np.min(self.y_vals), np.max(self.y_vals), 4)

        value1 = mapToBandedArea(np.mean(self.y_vals[0:9]), 0, delta, deltaHalfpoint)
        value2 = mapToBandedArea(np.mean(self.y_vals[10:]), 0, delta, deltaHalfpoint)

        self.f.write("S2:avgs= 1:" + str(value1) + " 2:" + str(value2) + "\n")

        modified_array = []

        for x in range(0, 10):
            modified_array.append(value1)
        for x in range(10, 20):
            modified_array.append(value2)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)

        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)

        self.f.write('\n')

        print ''


    def testAverageStepChanges(self):
        # S3:TL:kb We want to test the average step-changes example
        print 'Testing for S3:TL:kb'
        self.f.write('S3:TL:kb\n')

        min_value = np.min(self.y_vals)
        max_value = np.max(self.y_vals)

        delta, deltaHalfpoint = createBands(min_value, max_value, 4)

        xi = arange(1, 21)
        A = array([xi, ones(20)])
        # linearly generated sequence

        w = linalg.lstsq(A.T, self.y_vals)[0] # obtaining the parameters
        k = w[0]

        band_b = mapToBandedArea(w[0], min_value, delta, deltaHalfpoint)

        corrected_b = self.correctValue(band_b, deltaHalfpoint, max_value, min_value)

        if k >= 0.5:
            band_k = 0.75
        elif k >= 0:
            band_k = 0.25
        elif k >= -.5:
            band_k = -.25
        else:
            band_k = -.75

        corrected_k = band_k

        self.f.write("k = " + str(w[0]) + "\n")
        self.f.write("b = " + str(w[1]) + "\n")
        self.f.write("delta = " + str(delta) + "\n")
        self.f.write("halfpoint = " + str(deltaHalfpoint) + "\n")
        self.f.write("Band b = " + str(band_b) + "\n")
        self.f.write("Corr b = " + str(corrected_b) + "\n")
        self.f.write("Band k = " + str(band_k) + "\n")
        self.f.write("Corr k = " + str(corrected_k) + "\n")

        modified_array = []

        for x in range(1, 21):
            modified_array.append(corrected_k * x + corrected_b)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)

        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)

        self.f.write('\n')


    def testTrendLine(self):
        print 'Testing for S4:TL:pq'
        self.f.write('S4:TL:pq\n')
        xi = arange(1, 21)

        min_value = np.min(self.y_vals)
        max_value = np.max(self.y_vals)

        delta, deltaHalfpoint = createBands(min_value, max_value, 4)

        xi = arange(1, 21)
        A = array([xi, ones(20)])
        # linearly generated sequence

        w = linalg.lstsq(A.T, self.y_vals)[0] # obtaining the parameters
        fit = w[0] * xi + w[1]

        band_p = mapToBandedArea(fit[0], min_value, delta, deltaHalfpoint)
        band_q = mapToBandedArea(fit[len(fit) - 1], min_value, delta, deltaHalfpoint)
        corrected_p = self.correctValue(band_p, deltaHalfpoint, max_value, min_value)
        corrected_q = self.correctValue(band_q, deltaHalfpoint, max_value, min_value)

        yq_sub_yp = corrected_q - corrected_p

        xq_sub_xp = len(self.y_vals) - 1

        self.f.write("delta = " + str(delta) + "\n")
        self.f.write("halfpoint = " + str(deltaHalfpoint) + "\n")
        self.f.write('TL:p = ' + str(fit[0]) + "\n")
        self.f.write('TL:q = ' + str(fit[len(self.y_vals) - 1]) + "\n")
        self.f.write("Band_p = " + str(band_p) + "\n")
        self.f.write("Band_p = " + str(band_q) + "\n")
        self.f.write("Corr_p =" + str(corrected_p) + "\n")
        self.f.write("Corr_q =" + str(corrected_q) + "\n")
        self.f.write("yq-yp =" + str(yq_sub_yp) + "\n")
        self.f.write("xq-xp =" + str(xq_sub_xp) + "\n")

        modified_array = []

        for x in range(1, 21):
            modified_array.append(yq_sub_yp * (x - xi[0]) / xq_sub_xp + corrected_p)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)

        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)
        self.f.write('\n')
        print ''


    def testA2L(self):
        print "Testing for S5:a2L"
        self.f.write('S5:a2L\n')
        x_index = arange(1, 21)

        xa1 = (x_index[len(x_index) - 1] - x_index[0]) * 0.25 + x_index[0]
        xa2 = (x_index[len(x_index) - 1] - x_index[0]) * 0.75 + x_index[0]

        delta, deltaHalfpoint = createBands(np.min(self.y_vals), np.max(self.y_vals), 4)

        ya1 = mapToBandedArea(np.mean(self.y_vals[0:9]), 0, delta, deltaHalfpoint)
        ya2 = mapToBandedArea(np.mean(self.y_vals[10:]), 0, delta, deltaHalfpoint)

        self.f.write("xa1 = " + str(xa1) + "\n")
        self.f.write("xa1 = " + str(xa2) + "\n")
        self.f.write("ya1 = " + str(ya1) + "\n")
        self.f.write("ya1 = " + str(ya2) + "\n")
        self.f.write("ya2-ya1 = " + str(ya2 - ya1) + "\n")
        self.f.write("xa1-xa2 = " + str(xa1 - xa2) + "\n")


        modified_array = []

        for x in range(1, 21):
            modified_array.append((ya2 - ya1) * (x - xa1) / (xa2 - xa1) + ya1)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)

        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)

        self.f.write('\n')
        print ''

    def testF1FM(self):
        print "Testing for S6:f1fm"
        self.f.write('S6:f1fm\n')
        x_index = arange(1, 21)

        min_value = np.min(self.y_vals)
        max_value = np.max(self.y_vals)

        delta, deltaHalfpoint = createBands(min_value, max_value, 4)

        band_1 = mapToBandedArea((self.y_vals[0]), min_value, delta, deltaHalfpoint)
        band_2 = mapToBandedArea((self.y_vals[len(self.y_vals) - 1]), min_value, delta, deltaHalfpoint)

        xa1 = x_index[0]
        xa2 = x_index[len(x_index) - 1]

        ya1 = self.correctValue(band_1, deltaHalfpoint, max_value, min_value)
        ya2 = self.correctValue(band_2, deltaHalfpoint, max_value, min_value)

        self.f.write("Band_1 =" + str(band_1) + "\n")
        self.f.write("Band_2 =" + str(band_2) + "\n")
        self.f.write('xa1 =' + str(xa1) + "\n")
        self.f.write('xa2 =' + str(xa2) + "\n")
        self.f.write('ya1 =' + str(ya1) + "\n")
        self.f.write('ya2 =' + str(ya2) + "\n")
        self.f.write("ya2-ya1 = " + str(ya2 - ya1) + "\n")
        self.f.write("xa2-xa1 = " + str(xa2 - xa1) + "\n")

        modified_array = []

        for x in range(1, 21):
            modified_array.append((ya2 - ya1) * (x - xa1) / (xa2 - xa1) + ya1)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)
        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)

        self.f.write('\n')
        print ''

    def testF1AFM(self):
        print "Testing for S7:f1Afm"
        self.f.write('S7:f1Afm\n')

        x_index = arange(1, 21)

        min_value = np.min(self.y_vals)
        max_value = np.max(self.y_vals)

        avg = np.mean(self.y_vals)

        delta_a, deltaHalfpoint_a = createBands(min_value, max_value, 4)

        band_ya = mapToBandedArea(avg, min_value, delta_a, deltaHalfpoint_a)
        corrected_ya = self.correctValue(band_ya, deltaHalfpoint_a, max_value, min_value)

        delta_f, deltaHalfpoint_f = createBands(min_value, max_value, 2)

        band_1 = mapToBandedArea(self.y_vals[0], min_value, delta_f, deltaHalfpoint_f)
        corrected_1 = self.correctValue(band_1, deltaHalfpoint_f, max_value, min_value)

        band_2 = mapToBandedArea(self.y_vals[len(self.y_vals) - 1], min_value, delta_f, deltaHalfpoint_f)
        corrected_2 = self.correctValue(band_2, deltaHalfpoint_f, max_value, min_value)

        x_first = float(x_index[0])
        x_last = float(x_index[len(x_index) - 1])

        x_mid = (x_last - x_first) / 2 + x_first

        x_mid_sub_x1 = x_mid - x_first
        ya_sub_y1 = corrected_ya - corrected_1
        y2_sub_ya = corrected_2 - corrected_ya
        xm_sub_xmid = x_last - x_mid

        self.f.write('Band_ya =' + str(band_ya) + "\n")
        self.f.write('Band_1 =' + str(band_1) + "\n")
        self.f.write('corr_1 =' + str(corrected_1) + "\n")
        self.f.write('corr_ya =' + str(corrected_ya) + "\n")
        self.f.write('band_2 =' + str(band_2) + "\n")
        self.f.write('corr_2 =' + str(corrected_2) + "\n")
        self.f.write('xmid =' + str(x_mid) + "\n")
        self.f.write('xmid - self.y_vals =' + str(x_mid_sub_x1) + "\n")
        self.f.write('ya - y1 =' + str(ya_sub_y1) + "\n")
        self.f.write('y2 - ya =' + str(y2_sub_ya) + "\n")
        self.f.write('xm-xmid =' + str(xm_sub_xmid) + "\n")

        modified_array = []

        for x in range(1, 11):
            modified_array.append(ya_sub_y1 * (x - x_first) / x_mid_sub_x1 + corrected_1)

        for x in range(11, 21):
            modified_array.append(y2_sub_ya * (x - x_mid) / xm_sub_xmid + corrected_ya)

        self.calculateAverageDistance(self.y_vals, modified_array)
        self.calculateCorrelationCoeff(self.y_vals, modified_array)
        self.f.write('-- Reformed distribution array metrics')
        self.outputArrayMetrics(modified_array)
        self.f.write('\n')
        print ''


    def calculateAverageDistance(self, array1, array2):

        if len(array1) != len(array2):
            raise DifferentSizedArrayException()

        difference = 0
        for x in range(0, len(array1)):
            difference += np.absolute(array2[x] - array1[x])

        avgDifference = difference / len(array1)

        self.f.write('Distance = ' + str(avgDifference) + '\n')


    def calculateCorrelationCoeff(self, array1, array2):
        if len(array1) != len(array2):
            raise DifferentSizedArrayException()

        coefficient = np.corrcoef(array1, array2)[0][1]

        if not math.isnan(coefficient):
            coefficient = 1 - (coefficient + 1) / 2
        else:
            coefficient = 1

        self.f.write('Correlation coefficient = ' + str(coefficient) + '\n')


    def calculateArrayMetrics(self, array):
        mean = np.mean(array)
        stddev = np.std(array)
        min = np.min(array)
        max = np.max(array)

        return mean, stddev, min, max


    def outputArrayMetrics(self, array):
        mean, stddev, min, max = self.calculateArrayMetrics(array)
        self.f.write('\tMean = ' + str(mean) + '\n')
        self.f.write('\tMin = ' + str(min) + '\n')
        self.f.write('\tMax = ' + str(max) + '\n')
        self.f.write('\tStd deviation = ' + str(stddev) + '\n')


    def correctValue(self, band_ya, deltaHalfpoint_a, max_value, min_value):
        if band_ya < min_value:
            corrected_ya = min_value + deltaHalfpoint_a
        elif band_ya > max_value:
            corrected_ya = max_value - deltaHalfpoint_a
        else:
            corrected_ya = band_ya
        return corrected_ya


if __name__ == '__main__':
    unittest.main()

    #plotting the line
    #line = fit # regression line
    #plot(xi, line, 'r-', xi, x1, 'o')
    #show()