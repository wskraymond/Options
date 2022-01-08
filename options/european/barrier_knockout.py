from options.european.vanilla import *


class KnockoutOptions(Vanilla):
    def __init__(self, name, r, std, tenor, n, strike, opt, barrier, move):
        super().__init__(name, r, std, tenor, n, strike, opt)
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isTerminated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                          or (self.move == "down" and spot <= self.barrier)

    def __str__(self):
        return self.name

    def price(self, initSpot, noShares=100):
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
