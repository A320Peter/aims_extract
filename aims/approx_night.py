"""This module provides a function to give a _very_ quick and dirty
approximation of nighttime. It simply interpolates between the equinox
values for the UK using a cosine function. It is probably accurate to
within half an hour or so."""

import datetime
import math

sunset_dec21 = datetime.datetime(1, 1, 1, 15, 53)
sunset_jun21 = datetime.datetime(1, 1, 1, 21, 21)
sunset_maxoffset = (sunset_dec21 - sunset_jun21) / 2
sunset_mean = sunset_jun21 + sunset_maxoffset
sunrise_dec21 = datetime.datetime(1, 1, 1, 8, 4)
sunrise_jun21 = datetime.datetime(1, 1, 1, 4, 43)
sunrise_maxoffset = (sunrise_dec21 - sunrise_jun21) / 2
sunrise_mean = sunrise_jun21 + sunrise_maxoffset


def approx_night(d):
    """Returns a tuple consisting of two datetime.time objects
    representing (APPROX_SUNSET, APPROX_SUNRISE) for the date
    represented by datetime.date object D"""
    days_difference = (d.replace(2) - datetime.datetime(1, 12, 21)).days
    offset_factor = math.cos((days_difference * 2 * math.pi) / 365)
    sunset = sunset_mean + (sunset_maxoffset * int(offset_factor * 10000)) // 10000
    sunrise = sunrise_mean + (sunrise_maxoffset * int(offset_factor * 10000)) // 10000
    return (sunset.time(), sunrise.time())
