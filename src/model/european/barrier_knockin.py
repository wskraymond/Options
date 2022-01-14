import numpy as np
from src.model.european.vanilla import Vanilla


class KnockInOptions(Vanilla):
    def __init__(self, name, r, std, tenor, n, strike, opt, barrier, move):
        super().__init__(name, r, std, tenor, n, strike, opt)
        self.barrier = barrier
        self.move = move

        # check if terminated
        self._isActivated = lambda spot: (self.move == "up" and spot >= self.barrier) \
                                         or (self.move == "down" and spot <= self.barrier)

    def _dfs(self, initSpot, i, j, vanilla, memo):
        if i > self.n:
            return 0

        if memo[i][j] != -1:
            return memo[i][j]

        curr_spot = self.s(initSpot, i, j)

        if self._isActivated(curr_spot):
            return vanilla[i][j]

        memo[i][j] = self._f(self._dfs(initSpot, i + 1, j + 1, vanilla, memo), self._dfs(initSpot, i + 1, j, vanilla, memo))

        return memo[i][j]

    """
    1. Vanilla 2D numpy Array + DFS with memo
      * Time complexity: N^2 
      * Space complexity: N^2
    """
    def price(self, initSpot, noShares=100):
        memo = np.full((self.n + 1, self.n + 1), -1.0, dtype=np.longdouble)
        vanilla = super()._vanilla(initSpot, noShares)
        return self._dfs(initSpot, 0, 0, vanilla, memo)

    """
    2. Vanilla 2D numpy Array + Top-Down to de-/activate contract + Bottom-UP to reprice
      * Time complexity: N^2
      * Space complexity: Vanilla 2D numpy Array
    """
    """
    Failed to do so , same as vanilla price
    --------------------Input Parameter-----------------------------------------------------------
risk_free_rate= 0.009950330853168092 vol= 0.26236426446749106 N= 12 spot= 100.0 K= 95.0 T= 1.0 H= 105.0 shares= 1
--------------------Computation---------------------------------------------------------------
Vanilla Call PV at t=0:  13.524782674985937
Up-And-In Call PV at t=0:  13.524782674985937
Up-And-out Call PV at t=0:  0.15884558796031875
--------------------Equality for Knock-out + Knock-in = Vanilla --------------------------
knock_out_pv+knock_in_pv =  13.683628262946256 , vanilla_pv =  13.524782674985937 BS_Model= 13.370147046851775
--------------------End ------------------------------------------------------------------
    """
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

    # TODO: Approach 3
    """
    3. Bottom-up DP to calculate (1) activated node(i,j)'s vanilla price Or (2) if not activated, do as usual 
      * Time complexity: K x N^2
      * Space complexity: N (reuse the same maximum array)
    """
