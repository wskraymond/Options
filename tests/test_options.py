import math
import unittest
import scripts.barrier_options as options


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_up_and_out_call(self):
        N = 365
        upoutcall = options.KnockoutOptions("Up-And-Out Call",
                                            r=math.log(1+0.01),
                                            std=math.log(1+0.2),
                                            tenor=1.0,
                                            n=N,
                                            strike=95.0,
                                            opt="call",
                                            barrier=118.0,
                                            move="up")
        print("u=", upoutcall.u, "d=", upoutcall.d, "p=", upoutcall.p)
        print("spot cap at t=n: ", upoutcall.s(100.0, noUp=N, totalDown=N))
        print("PV at t=0: ", upoutcall.price(initSpot=100.0, noShares=100))

if __name__ == '__main__':
    unittest.main()
