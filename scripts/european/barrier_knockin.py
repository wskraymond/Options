import math
import numpy as np
from scripts.european.vanilla import *


class KnockInOptions(Vanilla):
    def __init__(self, name, r, std, tenor, n, strike, opt, barrier, move):
        super().__init__(name, r, std, tenor, n, strike, opt)
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isActivated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                         or (self.move == "down" and spot <= self.barrier)

    def __str__(self):
        return self.name

    def _dfs(self, initSpot, i, j, vanilla):
        if i>self.n:
            return 0

        curr_spot = self.s(initSpot, i, j)

        if self._isActivated(curr_spot):
            return vanilla[i][j]

        pv = self._f(self.dfs(initSpot,i+1, j+1, vanilla), self.dfs(initSpot, i+1,j, vanilla))

        return pv

    def price(self, initSpot, noShares=100):
        vanilla = super()._vanilla(initSpot, noShares)
        return self.dfs(initSpot, 0, 0, vanilla)


    #Failed to use bottom approach
    # def price(self, initSpot, noShares=100):
    #     pv = super()._vanilla(initSpot, noShares)
    #
    #     # clean up non-activated point
    #     # top-down traversal
    #     if not self._isActivated(initSpot):
    #         pv[0][0] == 0
    #         for i in range(1, self.n + 1):
    #             for j in range(i + 1):
    #                 spot = self.s(initSpot, totalDown=i, noUp=j)
    #                 # or (j >= i + 1 and activation[i - 1][j] == 1) or (j - 1 >= 0 and activation[i - 1][j - 1] == 1):
    #                 # no need to propagate
    #                 if not self._isActivated(spot):
    #                     pv[i][j] = 0
    #                 # else do nth ,becos it becomes vanilla at (i,j)
    #
    #         # reprice again
    #         for i in reversed(range(self.n)):
    #             for j in range(i + 1):
    #                 # trick: only recalculate those non-activated node through bottom-up traversal
    #                 if pv[i][j] == 0:
    #                     pv[i][j] = self._f(pvUp=pv[i + 1][j + 1], pvDown=pv[i + 1][j])
    #
    #     return pv[0][0]
