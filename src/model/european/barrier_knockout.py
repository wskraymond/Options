import numpy as np

from src.model.european import logger
from src.model.european.vanilla import Vanilla


class KnockoutOptions(Vanilla):
    def __init__(self, name, r, std, tenor, n, strike, opt, barrier, move, fast=True):
        super().__init__(name, r, std, tenor, n, strike, opt, fast)
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isTerminated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                          or (self.move == "down" and spot <= self.barrier)

    @logger
    def price(self, initSpot, noShares=100):
        if self.fast:
            return self._fast_price(initSpot, noShares)
        else:
            return self._slow_price(initSpot, noShares)

    def _fast_price(self, initSpot, noShares=100):
        # S: size=N+1
        S = initSpot * self.u ** np.arange(0, self.n + 1, 1) * self.d ** np.arange(self.n, -1, -1)

        # initialize PV(1D array): size=N+1
        if self.opt == "call":
            PV = np.maximum(S - self.strike, 0) * noShares
        elif self.opt == "put":
            PV = np.maximum(self.strike - S, 0) * noShares
        else:
            raise ValueError("Invalid option type", self.opt)

        PV[((self.move == "up") & (S >= self.barrier))
           | ((self.move == "down") & (S <= self.barrier))] = 0

        # n-1...0
        for i in reversed(range(self.n)):
            # no new copy
            # assign result to the view of PV
            PV[:i + 1] = self.df * (self.pu * PV[1:i + 2] + self.pd * PV[0:i + 1])
            # shrink
            PV = PV[:-1]
            # PV: new size = i
            S = initSpot * self.u ** np.arange(0, i + 1, 1) * self.d ** np.arange(i, -1, -1)
            PV[((self.move == "up") & (S >= self.barrier))
               | ((self.move == "down") & (S <= self.barrier))] = 0

        return PV[0]

    def _slow_price(self, initSpot, noShares=100):
        pv = np.zeros(self.n + 1, dtype=np.longdouble)

        # base case - check if it's already been terminated
        if self._isTerminated(initSpot):
            return 0  # terminated contract

        # base case - PV(n-1)
        for j in range(self.n + 1):
            spot = self.s(initSpot, totalDown=self.n, noUp=j)
            if not self._isTerminated(spot):
                if self.opt == "call":
                    pv[j] = max(0.0, spot - self.strike) * noShares
                else:
                    pv[j] = max(0.0, self.strike - spot) * noShares
            else:
                pv[j] = 0.0

        for i in reversed(range(self.n)):
            for j in range(i + 1):
                spot = self.s(initSpot, totalDown=i, noUp=j)
                if self._isTerminated(spot):
                    pv[j] = 0.0
                else:
                    pv[j] = self._f(pvUp=pv[j + 1], pvDown=pv[j])

        return pv[0]
