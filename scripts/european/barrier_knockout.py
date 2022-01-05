import math
import numpy as np


class KnockoutOptions:
    style = "European"

    def __init__(self, name, r, std, tenor, n, strike, opt, barrier, move):
        self.name = name
        self.tenor = tenor
        self.n = n
        self.h = self.tenor / self.n
        self.r = r
        self.df = math.exp(-self.h * self.r)
        self.std = std
        self.u = math.exp(math.sqrt(self.h) * self.std)
        self.d = 1 / self.u
        self.p = (1/self.df - self.d) / (self.u - self.d)
        self.strike = strike
        self.opt = opt
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isTerminated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                          or (self.move == "down" and spot <= self.barrier)

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: self.df * (self.p * pvUp + (1 - self.p) * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: initSpot * math.pow(self.u, math.sqrt(noUp)) * math.pow(self.d,
                                                                                                math.sqrt(totalDown - noUp))

    def __str__(self):
        return self.name

    def price(self, initSpot, noShares=100):
        pv = np.zeros(self.n + 1)

        # base case - check if it's already been terminated
        if self._isTerminated(initSpot):
            return 0 #terminated contract

        # base case - PV(n-1)
        for j in range(self.n + 1):
            spot = self.s(initSpot, totalDown=self.n, noUp=j)
            if not self._isTerminated(spot):
                if self.opt == "call":
                    pv[j] = max(0, spot - self.strike) * noShares
                else:
                    pv[j] = max(0, self.strike - spot) * noShares

        for i in reversed(range(self.n)):
            for j in range(i + 1):
                spot = self.s(initSpot, totalDown=i, noUp=j)
                if self._isTerminated(spot):
                    pv[j] = 0
                else:
                    pv[j] = self._f(pvUp=pv[j + 1], pvDown=pv[j])

        return pv[0]
