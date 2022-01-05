import math
import numpy as np


class KnockInOptions:
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
        self.p = (1 / self.df - self.d) / (self.u - self.d)
        self.strike = strike
        self.opt = opt
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isActivated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                         or (self.move == "down" and spot <= self.barrier)

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: self.df * (self.p * pvUp + (1 - self.p) * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: initSpot * math.pow(self.u, math.sqrt(noUp)) * math.pow(self.d,
                                                                                                           math.sqrt(
                                                                                                               totalDown - noUp))

    def __str__(self):
        return self.name

    def _vanilla(self, initSpot, noShares=100):
        # pv(i,j)
        pv = np.zeros((self.n + 1, self.n + 1))

        # base case - PV(n-1)
        for j in range(self.n + 1):
            spot = self.s(initSpot, totalDown=self.n, noUp=j)
            if self.opt == "call":
                pv[self.n][j] = max(0, spot - self.strike) * noShares
            else:
                pv[self.n][j] = max(0, self.strike - spot) * noShares

        # Vanilla price
        for i in reversed(range(self.n)):
            for j in range(i + 1):
                pv[i][j] = self._f(pvUp=pv[i + 1][j + 1], pvDown=pv[i + 1][j])

        return pv

    def price(self, initSpot, noShares=100):
        pv = self._vanilla(initSpot, noShares)

        # clean up non-trigger pv
        # top-down traversal
        activation = np.zeros((self.n + 1, self.n + 1))
        if not self._isActivated(initSpot):
            pv[0][0] == 0
            for i in range(1, self.n + 1):
                for j in range(i + 1):
                    spot = self.s(initSpot, totalDown=i, noUp=j)
                    # or (j >= i + 1 and activation[i - 1][j] == 1) or (j - 1 >= 0 and activation[i - 1][j - 1] == 1):
                    # not need to propagate
                    if self._isActivated(spot):
                        activation[i][j] = 1
                    else:
                        pv[i][j] = 0

            # reprice again
            for i in reversed(range(self.n)):
                for j in range(i + 1):
                    if pv[i][j] == 0: # only recalculate those node might not be triggered
                        pv[i][j] = self._f(pvUp=pv[i + 1][j + 1], pvDown=pv[i + 1][j])

        return pv[0][0]
