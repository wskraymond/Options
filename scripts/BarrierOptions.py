import math


class BarrierOptions:

    def __init__(self, id, r, std, tenor, n, strike, opt, barrier, brt):
        self.id = id
        self.tenor = tenor
        self.n = n
        self.h = self.tenor/self.n
        self.r = r
        self.df = math.exp(self.h*self.r)
        self.std = std
        self.u = math.exp(math.sqrt(self.h)*self.h)
        self.d = 1/self.u
        self.p = (self.df-self.d)/(self.u - self.d)
        self.strike = strike
        self.opt = opt
        self.barrier = barrier
        self.brt = brt

    def __str__(self):
        return self.id

    def price(self, initSpot):
        #base case
        dp = []

        #s(i,j) = s0 * u^j * d^i-j
        for j in range(self.n):
            spot = initSpot*math.pow(self.u,j)*math.pow(self.d, self.n-1-j)
            if self.opt == "call":
                dp[self.n-1][j] = max(0, spot-self.strike)
            elif self.opt == "put":
                dp[self.n-1][j] = max(0, self.strike-spot)
            else:
                raise ValueError("Invalid options type(call, put)", self.opt)

        price = .0


        return price
