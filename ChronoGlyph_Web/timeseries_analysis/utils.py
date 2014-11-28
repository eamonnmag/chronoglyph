import numpy

__author__ = 'eamonnmaguire'


def createBands(min, max, bands):
    """
        Creates a band for the series on the y-axis defined by a delta indicating the steps to use in creating the banding
        and a mid-point to give a value for that value when mapped
    """
    delta = (max - min) / float(bands)
    deltaHalfpoint = delta / 2.0

    return delta, deltaHalfpoint


def mapToBandedArea(value, min, delta, halfpoint):
    """
    Rounds the values to an area of the band it is present in
    """
    roundedValue = numpy.round((value - min - halfpoint) / delta, 0)
    return roundedValue * delta + min + halfpoint


def normalize(x, epsilon):
    """
    Function will normalize an array (give it a mean of 0, and a
    standard deviation of 1) unless it's standard deviation is below
    epsilon, in which case it returns an array of zeros the length
    of the original array.
    """
    X = numpy.asanyarray(x)
    if X.std() < epsilon:
        return [0 for entry in X]
    return (X - X.mean()) / X.std()


class DifferentSizedArrayException(Exception):
    pass
