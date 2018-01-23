#!/usr/bin/env python
""" atmosCalc is used to compute atmospheric
    properties using 1976 standard atmosphere"""
import os
import subprocess
from pandas import read_table
import numpy as np
import units

__author__ = "Cameron Flannery"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "alpha"

DEBUG = True

def ratios(alt):
    """ expects altitude in meters """
    if alt < 0:
        raise ValueError('Altitude must be greater than 0')
    # ============================================================================
    # LOCAL CONSTANTS
    # ============================================================================
    REARTH = 6369000.0      # radius of Earth (m)
    GMR = 0.034163195       # hydrostatic constant K/m
    NTAB = 8                # number of entries in the defining tables
    # ============================================================================
    # CREATE DATAFRAME (1976 STD. ATMOSPHERE)
    # ============================================================================
    path = os.path.join(os.path.dirname(__file__), 'assets', 'atmosData.csv')
    df = read_table(path, delimiter=',', header=1,
                    dtype={'h(m)': np.float64, 'P(Pascal)': np.float64,
                           'T(K)': np.float64, 'dT(K/m)': np.float64})
    # * * * * * * * * * * * * * * Headers * * * * * * * * * * * * * *
    # i	h(m)	h(ft)	P(pascal)	P(inHg)	T(K)	dT(K/m)	dT(K/ft)
    h = alt*REARTH/(alt+REARTH)  # convert geometric to geopotential altitude
    htab = df['h(m)']       # create array with geopotential altitudes (m)
    gtab = df['dT(K/m)']    # Temperature Lapse Rate (K/m)
    ttab = df['T(K)']       # Standard Temperature (K)
    ptab = df['P(Pascal)']  # Static Pressure (Pascals)


    # Binary Search through htab data
    i = 0
    j = NTAB
    try:
        while True:
            k = (i+j)//2  # integer division
            if h < htab[k]:
                j = k
            else:
                i = k
            if j <= i+1:
                break
    except KeyError:
        return (0.0, 0.0, 0.0)

    tgrad = gtab[i]                                   # i will be in 1...NTAB-1
    tbase = ttab[i]
    deltah = h - htab[i]
    tlocal = tbase+tgrad*deltah  # local temperature
    theta = tlocal / ttab[0]  # ratio of temperature to sea-level temperature

    # delta =: ratio of pressure to sea-level pressure
    if tgrad == 0.0:
        delta = ptab[i] * np.exp(-GMR*deltah/tbase) / ptab[0]
    else:
        delta = ptab[i] * (tbase/tlocal)**(GMR/tgrad) / ptab[0]

    sigma = delta/theta  # ratio of density to sea-level density

    return (sigma, delta, theta)

def pressure(alt, uni=False):
    sea_level_pressure = units.Value(101325, 'Pa')
    if uni == False and type(alt) != units.Value:
        raise TypeError('units is a required argument when argument is not units.Value types')
    
    [sigma, delta, theta] = ratios(alt.SIValue)
    return sea_level_pressure*delta

def temperature(alt, uni=False):
    sea_level_temperature = units.Value(298, 'K')
    if uni == False and type(alt) != units.Value:
        raise TypeError('units is a required argument when argument is not units.Value types')
    
    [sigma, delta, theta] = ratios(alt.SIValue)
    return sea_level_temperature*theta

def density(alt, uni=False):
    sea_level_density = units.Value(1.29, ['kg','m^3'])
    if uni == False and type(alt) != units.Value:
        raise TypeError('units is a required argument when argument is not units.Value types')
    
    [sigma, delta, theta] = ratios(alt.SIValue)
    return sea_level_density*sigma

def test():
    print(pressure(units.Value(10000,'m')))
    print(temperature(units.Value(10000,'m')))
    print(density(units.Value(10000,'m')))


if __name__ == '__main__':
    try:
        subprocess.call('clear')
    except OSError:
        subprocess.call('cls', shell=True)
    if DEBUG:
        test()
