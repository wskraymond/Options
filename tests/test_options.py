import math
import unittest
from scripts.european.barrier_knockout import *
from scripts.european.barrier_knockin import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_up_and_out_call(self):
        N = 365
        spot=100.0
        options = KnockoutOptions("Up-And-Out Call",
                                            r=math.log(1+0.01),
                                            std=math.log(1+0.2),
                                            tenor=1.0,
                                            n=N,
                                            strike=95.0,
                                            opt="call",
                                            barrier=118.0,
                                            move="up")
        print("u=", options.u, "d=", options.d, "p=", options.p)
        print("spot cap at t=n: ", options.s(spot, noUp=N, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_down_and_out_put(self):
        N = 365
        spot = 95.0
        options = KnockoutOptions("Up-And-Out Call",
                                            r=math.log(1+0.01),
                                            std=math.log(1+0.2),
                                            tenor=1.0,
                                            n=N,
                                            strike=100.0,
                                            opt="put",
                                            barrier=92.0,
                                            move="down")
        print("u=", options.u, "d=", options.d, "p=", options.p)
        print("spot floor at t=n: ", options.s(spot, noUp=0, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_up_and_in_call(self):
        N = 365
        spot = 90
        options = KnockInOptions("Up-And-In Call",
                                            r=math.log(1+0.01),
                                            std=math.log(1+0.2),
                                            tenor=1.0,
                                            n=N,
                                            strike=80.0,
                                            opt="call",
                                            barrier=92.0,
                                            move="up")
        print("u=", options.u, "d=", options.d, "p=", options.p)
        print("spot cap at t=n: ", options.s(spot, noUp=N, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_down_and_in_put(self):
        N = 365
        spot = 95
        options = KnockInOptions("Up-And-In Call",
                                            r=math.log(1+0.01),
                                            std=math.log(1+0.2),
                                            tenor=1.0,
                                            n=N,
                                            strike=100.0,
                                            opt="put",
                                            barrier=92.0,
                                            move="down")
        print("u=", options.u, "d=", options.d, "p=", options.p)
        print("spot floor at t=n: ", options.s(spot, noUp=0, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

if __name__ == '__main__':
    unittest.main()
