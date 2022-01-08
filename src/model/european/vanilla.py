import numpy as np
from src.model.european.derivatives import *
from scipy.stats import norm


class Vanilla(Derivatives):
    style = "European"

    def __init__(self, name, r, std, tenor, n, strike, opt, model="CRR"):
        self.name = name
        self.tenor = tenor
        self.n = n
        self.r = r
        self.std = std
        self.strike = strike
        self.opt = opt
        self.model = model
        if model == "CRR":
            self._crr()
        elif model == "JR":
            self._jr()
        elif model == "TRG":
            self._trg()
        elif model == "BS":
            self._bs()
        else:
            raise ValueError("Invalid Model(CRR or TRG)")

    def _crr(self):
        self.h = self.tenor / self.n
        self.df = np.exp(-self.h * self.r)
        self.u = np.exp(np.sqrt(self.h) * self.std)
        self.d = 1.0 / self.u
        self.pu = (1.0 / self.df - self.d) / (self.u - self.d)
        self.pd = 1.0 - self.pu

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: \
            self.df * (self.pu * pvUp + self.pd * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: \
            initSpot * self.u ** noUp * self.d ** (totalDown - noUp)

    def _jr(self):
        self.h = self.tenor / self.n
        self.df = np.exp(-self.h * self.r)
        nu = self.r - 0.5 * self.std ** 2
        self.u = np.exp(nu * self.h + self.std * np.sqrt(self.h))
        self.d = np.exp(nu * self.h - self.std * np.sqrt(self.h))
        self.pu = 0.5
        self.pd = 1.0 - self.pu

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: \
            self.df * (self.pu * pvUp + self.pd * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: \
            initSpot * self.u ** noUp * self.d ** (totalDown - noUp)

    def _trg(self):
        self.h = self.tenor / self.n
        self.df = np.exp(-self.h * self.r)

        nu = self.r - 0.5 * self.std ** 2
        self.u = np.sqrt(self.std ** 2 * self.h + nu ** 2 * self.h ** 2)
        self.d = -self.u
        self.pu = 0.5 + 0.5 * nu * self.h / self.u
        self.pd = 1 - self.pu

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: \
            self.df * (self.pu * pvUp + self.pd * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: \
            initSpot * np.exp(self.u * noUp) * np.exp(self.d * (totalDown - noUp))

    def _bs(self):
        # common
        self.ttm = lambda t: self.tenor - t
        self.d1 = lambda St, t: (1.0 / (self.std * np.sqrt(self.ttm(t)))) * (
                np.log(St / self.strike) + (self.r + self.std ** 2.0 / 2.0) * self.ttm(t))
        self.d2 = lambda d1, t: d1 - self.std * np.sqrt(self.ttm(t))
        self.pv_k = lambda t: self.strike * np.exp(-self.r * self.ttm(t))
        self.n2_call = lambda d2: norm.cdf(d2)
        self.n2_put = lambda d2: self.n2_call(d2) - 1

        # greek
        self._delta_call = lambda d1: norm.cdf(d1, 0, 1)
        self._delta_put = lambda d1: self._delta_call(d1) - 1
        self._gamma = lambda d1, St, t: norm.pdf(d1, 0, 1) / (St * self.std * np.sqrt(self.ttm(t)))
        self._vega = lambda d1, St, t: St * norm.pdf(d1, 0, 1) * np.sqrt(self.ttm(t))
        self._theta = lambda d1, St, t, N2, pv_k: -(St * norm.pdf(d1, 0, 1) * self.std) / (
                2 * np.sqrt(self.ttm(t))) - self.r * N2 * pv_k
        self._rho = lambda N2, t, pv_k: self.ttm(t) * pv_k * N2

        # PV
        self._bs = lambda delta, St, N2, pv_k: delta * St - N2 * pv_k

    def __str__(self):
        return self.name

    def _vanilla(self, initSpot, noShares=100):
        # pv(i,j)
        pv = np.zeros((self.n + 1, self.n + 1), dtype=np.longdouble)

        # base case - PV(n-1)
        for j in range(self.n + 1):
            spot = self.s(initSpot, totalDown=self.n, noUp=j)
            if self.opt == "call":
                pv[self.n][j] = max(0, spot - self.strike) * noShares
            else:
                pv[self.n][j] = max(0, self.strike - spot) * noShares

        """
        version 1
        for i in np.arange(N-1,-1,-1):            //N-1……….0  => total loop N times
                for j in range(0,i+1):            //0…N-1, 0…..N-2, 0…..N-3,....., 0
        
        version 2
        for i in np.arange(N, 0, -1):             //N………1         => total loop N times
                for j in range(0, i):             //0….N-1, 0…..N-2,0…...N-3,....., 0
                
        version 3
        for i in reversed(range(N)):              //range(N) -> 0…….N-1 ->reversed -> N-1……0 
               for j in range(i + 1):             //0…N-1, 0…..N-2, 0…..N-3,....., 0
        """
        # Vanilla price
        for i in reversed(range(self.n)):
            for j in range(i + 1):
                pv[i][j] = self._f(pvUp=pv[i + 1][j + 1], pvDown=pv[i + 1][j])

        return pv

    def price(self, initSpot, noShares=100):
        if self.model == "BS":
            return self._bs_price(initSpot, noShares)
        else:
            pv = self._vanilla(initSpot, noShares)
            return pv[0][0]

    def _bs_price(self, initSpot, noShares=100):
        d1 = self.d1(initSpot, 0)
        d2 = self.d2(d1, 0)
        pv_k = self.pv_k(t=0)
        if self.opt == "call":
            delta = self._delta_call(d1)
            N2 = self.n2_call(d2)
        elif self.opt == "put":
            delta = self._delta_put(d1)
            N2 = self.n2_put(d2)
        else:
            raise ValueError("Invalid Options Type ", self.opt)

        return self._bs(delta=delta, St=initSpot, N2=N2, pv_k=pv_k) * noShares

    def delta(self, initSpot, noShares=100):
        d1 = self.d1(initSpot, 0)
        if self.opt == "call":
            return self._delta_call(d1) * noShares
        elif self.opt == "put":
            return self._delta_put(d1) * noShares
        else:
            raise ValueError("Invalid Options Type ", self.opt)

    def gamma(self, initSpot, noShares=100):
        d1 = self.d1(initSpot, 0)
        if self.opt == "call" or self.opt == "put":
            return self._gamma(d1=d1, St=initSpot, t=0) * noShares
        else:
            raise ValueError("Invalid Options Type ", self.opt)

    def vega(self, initSpot, noShares=100, unit="pct"):
        d1 = self.d1(initSpot, 0)
        if self.opt == "call" or self.opt == "put":
            vega = self._vega(d1, St=initSpot, t=0) * noShares
            if unit == "pct":
                vega = 0.01 * vega

            return vega
        else:
            raise ValueError("Invalid Options Type ", self.opt)

    def theta(self, initSpot, noShares=100, unit="day"):
        d1 = self.d1(initSpot, 0)
        d2 = self.d2(d1, 0)
        pv_k = self.pv_k(t=0)
        if self.opt == "call":
            N2 = self.n2_call(d2)
        elif self.opt == "put":
            N2 = self.n2_put(d2)
        else:
            raise ValueError("Invalid Options Type ", self.opt)

        theta = self._theta(d1=d1, St=initSpot, t=0, N2=N2, pv_k=pv_k) * noShares
        if unit == "day":
            theta = theta / 365

        return theta

    def rho(self, initSpot, noShares=100, unit="pct"):
        d1 = self.d1(initSpot, 0)
        d2 = self.d2(d1, 0)
        pv_k = self.pv_k(t=0)
        if self.opt == "call":
            N2 = self.n2_call(d2)
        elif self.opt == "put":
            N2 = self.n2_put(d2)
        else:
            raise ValueError("Invalid Options Type ", self.opt)

        rho = self._rho(N2=N2, t=0, pv_k=pv_k) * noShares
        if unit == "pct":
            rho = 0.01 * rho

        return rho
