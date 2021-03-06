import unittest

import math
import numpy as np
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import delta, gamma, vega, theta, rho
import matplotlib.pyplot as plt

from src.model.european.barrier_knockin import KnockInOptions
from src.model.european.barrier_knockout import KnockoutOptions
from src.model.european.vanilla import Vanilla


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # S = np.arange(10)
        # a = True
        # print(a & (S > 4))
        # print(S[(S > 4) & (S < 8)])
        self.assertEqual(True, True)  # add assertion here

    def test_up_and_out_call(self):
        N = 12
        spot = 100.0
        shares = 100
        options = KnockoutOptions("Up-And-Out Call",
                                  r=math.log(1 + 0.01),
                                  std=math.log(1 + 0.3),
                                  tenor=1.0,
                                  n=N,
                                  strike=95.0,
                                  opt="call",
                                  barrier=105.0,
                                  move="up")
        print("spot cap at t=n: ", options.s(spot, noUp=N, totalDown=N))
        print(options, "PV at t=0: ", options.price(initSpot=spot, noShares=shares))

        options = Vanilla("Call",
                          r=math.log(1 + 0.01),
                          std=math.log(1 + 0.3),
                          tenor=1.0,
                          n=N,
                          strike=95.0,
                          opt="call")
        print("spot cap at t=n: ", options.s(spot, noUp=N, totalDown=N))
        print(options, "PV at t=0: ", options.price(initSpot=spot, noShares=shares))

    def test_down_and_out_put(self):
        N = 12
        spot = 95.0
        options = KnockoutOptions("Up-And-Out Call",
                                  r=math.log(1 + 0.01),
                                  std=math.log(1 + 0.2),
                                  tenor=1.0,
                                  n=N,
                                  strike=100.0,
                                  opt="put",
                                  barrier=92.0,
                                  move="down")
        print("spot floor at t=n: ", options.s(spot, noUp=0, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_up_and_in_call(self):
        N = 12
        spot = 90
        options = KnockInOptions("Up-And-In Call",
                                 r=math.log(1 + 0.01),
                                 std=math.log(1 + 0.2),
                                 tenor=1.0,
                                 n=N,
                                 strike=80.0,
                                 opt="call",
                                 barrier=92.0,
                                 move="up")
        print("spot cap at t=n: ", options.s(spot, noUp=N, totalDown=N))
        print("PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_down_and_in_put(self):
        N = 12
        spot = 95
        options = KnockInOptions("Up-And-In Call",
                                 r=math.log(1 + 0.01),
                                 std=math.log(1 + 0.2),
                                 tenor=1.0,
                                 n=N,
                                 strike=100.0,
                                 opt="put",
                                 barrier=92.0,
                                 move="down")
        print("spot floor at t=n: ", options.s(spot, noUp=0, totalDown=N))
        print(options, "PV at t=0: ", options.price(initSpot=spot, noShares=100))

        options = Vanilla("Call",
                          r=math.log(1 + 0.01),
                          std=math.log(1 + 0.2),
                          tenor=1.0,
                          n=N,
                          strike=100.0,
                          opt="put")
        print("spot floor at t=n: ", options.s(spot, noUp=0, totalDown=N))
        print(options, "PV at t=0: ", options.price(initSpot=spot, noShares=100))

    def test_knockin_knockout_parity(self):
        risk_free_rate = math.log(1 + 0.01)
        vol = math.log(1 + 0.3)
        N = 500
        spot = 100.0
        K = 95.0
        T = 1.0
        H = 105.0
        shares = 1

        print()
        print("--------------------Input Parameter-----------------------------------------------------------")
        print("risk_free_rate=", risk_free_rate, "vol=", vol, "N=", N, "spot=", spot, "K=", K, "T=", T, "H=", H,
              "shares=", shares)

        print("--------------------Computation---------------------------------------------------------------")
        BS = bs('c', spot, K, T, risk_free_rate, vol)

        vanilla = Vanilla("Vanilla Call",
                          r=risk_free_rate,
                          std=vol,
                          tenor=T,
                          n=N,
                          strike=K,
                          opt="call")
        # print("spot cap at t=n: ", vanilla.s(spot, noUp=N, totalDown=N))
        vanilla_pv = vanilla.price(initSpot=spot, noShares=shares)
        print(vanilla, "PV at t=0: ", vanilla_pv)

        knock_in = KnockInOptions("Up-And-In Call",
                                  r=risk_free_rate,
                                  std=vol,
                                  tenor=T,
                                  n=N,
                                  strike=K,
                                  opt="call",
                                  barrier=H,
                                  move="up")
        # print("spot cap at t=n: ", knock_in.s(spot, noUp=N, totalDown=N))
        knock_in_pv = knock_in.price(initSpot=spot, noShares=shares)
        print(knock_in, "PV at t=0: ", knock_in_pv)

        knock_out = KnockoutOptions("Up-And-out Call",
                                    r=risk_free_rate,
                                    std=vol,
                                    tenor=T,
                                    n=N,
                                    strike=K,
                                    opt="call",
                                    barrier=H,
                                    move="up")
        # print("spot cap at t=n: ", knock_out.s(spot, noUp=N, totalDown=N))
        knock_out_pv = knock_out.price(initSpot=spot, noShares=shares)
        print(knock_out, "PV at t=0: ", knock_out_pv)

        print("--------------------Equality for Knock-out + Knock-in = Vanilla --------------------------")
        print("knock_out_pv+knock_in_pv = ", knock_out_pv + knock_in_pv, ", vanilla_pv = ", vanilla_pv, "BS_Model=", BS)
        self.assertAlmostEqual(knock_out_pv + knock_in_pv, vanilla_pv)
        self.assertAlmostEqual(bs('c', spot, K, T, risk_free_rate, vol), vanilla_pv, delta=0.01)
        print("--------------------End ------------------------------------------------------------------")

    def test_convergence(self):
        # Initialise parameters
        S0 = 100  # initial stock price
        K = 110  # strike price
        T = 0.5  # time to maturity in years
        r = np.log(1 + 0.06)  # annual risk-free rate
        sigma = np.log(1 + 0.3)  # Annualised stock price volatility

        CRR, TRG, TRG2, JR = [], [], [], []

        periods = range(10, 500, 10)
        for N in periods:
            trg_model = Vanilla("Call",
                                r=r,
                                std=sigma,
                                tenor=T,
                                n=N,
                                strike=K,
                                opt="call",
                                model="TRG")
            TRG.append(trg_model.price(initSpot=S0, noShares=1))

            jr_model = Vanilla("Call",
                               r=r,
                               std=sigma,
                               tenor=T,
                               n=N,
                               strike=K,
                               opt="call",
                               model="JR")
            JR.append(jr_model.price(initSpot=S0, noShares=1))

            crr_model = Vanilla("Call",
                                r=r,
                                std=sigma,
                                tenor=T,
                                n=N,
                                strike=K,
                                opt="call",
                                model="CRR")
            CRR.append(crr_model.price(initSpot=S0, noShares=1))

        BS = [bs('c', S0, K, T, r, sigma) for i in periods]

        # uncomment to show
        # plt.plot(periods, JR, label='Jarrow_Rudd')
        # plt.plot(periods, CRR, label='Cox, Ross and Rubinstein')
        # plt.plot(periods, TRG, 'r--', label='Trigeorgis')
        # plt.plot(periods, BS, 'k', label='Black-Scholes')
        # plt.legend(loc='upper right')
        # plt.show()

    def test_bs_call(self):
        S0 = 100  # initial stock price
        K = 110  # strike price
        T = 0.5  # time to maturity in years
        r = np.log(1 + 0.06)  # annual risk-free rate
        sigma = np.log(1 + 0.3)  # Annualised stock price volatility

        bs_model = Vanilla("Call",
                           r=r,
                           std=sigma,
                           tenor=T,
                           n=None,
                           strike=K,
                           opt="call",
                           model="BS")

        expected = bs('c', S0, K, T, r, sigma)
        self.assertAlmostEqual(expected, bs_model.price(S0, 1))

    def test_bs_call(self):
        S0 = 100  # initial stock price
        K = 110  # strike price
        T = 0.5  # time to maturity in years
        r = np.log(1 + 0.06)  # annual risk-free rate
        sigma = np.log(1 + 0.3)  # Annualised stock price volatility

        bs_model = Vanilla("Call",
                           r=r,
                           std=sigma,
                           tenor=T,
                           n=None,
                           strike=K,
                           opt="call",
                           model="BS")

        self.assertAlmostEqual(bs('c', S0, K, T, r, sigma), bs_model.price(S0, 1))
        self.assertAlmostEqual(delta('c', S0, K, T, r, sigma), bs_model.delta(S0, 1))
        self.assertAlmostEqual(gamma('c', S0, K, T, r, sigma), bs_model.gamma(S0, 1))
        self.assertAlmostEqual(vega('c', S0, K, T, r, sigma), bs_model.vega(S0, 1))
        self.assertAlmostEqual(theta('c', S0, K, T, r, sigma), bs_model.theta(S0, 1))
        self.assertAlmostEqual(rho('c', S0, K, T, r, sigma), bs_model.rho(S0, 1))

    def test_bs_put(self):
        S0 = 100  # initial stock price
        K = 110  # strike price
        T = 0.5  # time to maturity in years
        r = np.log(1 + 0.06)  # annual risk-free rate
        sigma = np.log(1 + 0.3)  # Annualised stock price volatility

        bs_model = Vanilla("Call",
                           r=r,
                           std=sigma,
                           tenor=T,
                           n=None,
                           strike=K,
                           opt="put",
                           model="BS")

        self.assertAlmostEqual(bs('p', S0, K, T, r, sigma), bs_model.price(S0, 1))
        self.assertAlmostEqual(delta('p', S0, K, T, r, sigma), bs_model.delta(S0, 1))
        self.assertAlmostEqual(gamma('p', S0, K, T, r, sigma), bs_model.gamma(S0, 1))
        self.assertAlmostEqual(vega('p', S0, K, T, r, sigma), bs_model.vega(S0, 1))
        self.assertAlmostEqual(theta('p', S0, K, T, r, sigma), bs_model.theta(S0, 1))
        self.assertAlmostEqual(rho('p', S0, K, T, r, sigma), bs_model.rho(S0, 1))

    def test_knockout_fast_slow_version(self):
        risk_free_rate = math.log(1 + 0.01)
        vol = math.log(1 + 0.3)
        spot = 100.0
        K = 95.0
        T = 1.0
        H = 105.0
        shares = 1

        print()
        print("--------------------Input Parameter-----------------------------------------------------------")
        print("risk_free_rate=", risk_free_rate, "vol=", vol, "spot=", spot, "K=", K, "T=", T, "H=", H,
              "shares=", shares)

        print("--------------------Logger---------------------------------------------------------------")
        for N in [3,50, 100, 1000, 5000]:
            slow = KnockoutOptions("Up-And-out Call",
                                        r=risk_free_rate,
                                        std=vol,
                                        tenor=T,
                                        n=N,
                                        strike=K,
                                        opt="call",
                                        barrier=H,
                                        move="up",
                                        fast=False)

            fast = KnockoutOptions("Up-And-out Call",
                                   r=risk_free_rate,
                                   std=vol,
                                   tenor=T,
                                   n=N,
                                   strike=K,
                                   opt="call",
                                   barrier=H,
                                   move="up",
                                   fast=True)
            s_pv = slow.price(initSpot=spot, noShares=shares)
            f_pv = fast.price(initSpot=spot, noShares=shares)
            self.assertAlmostEqual(s_pv, f_pv)

if __name__ == '__main__':
    unittest.main()
