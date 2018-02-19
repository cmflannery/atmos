from __future__ import division, absolute_import, print_function
from atmos import *
import units


def test_pressure():
    tester = atmos.SimpleAtmos()
    tester.alt = units.Value(1000,'m')
    assert(1==1)
    assert(tester.pressure()==tester.pressure(alt=units.Value(1000,'m')))
    # assert(tester.pressure()==tester.pressure(alt=units.Value(1000,'m')))
    # assert(tester.pressure()==tester.pressure(alt=1000, uni='m'))