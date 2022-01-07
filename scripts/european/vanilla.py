import math
import numpy as np
from scripts.european.derivatives import *


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
        if model == "CRR":
            self._crr()
        elif model == "JR":
            self._jr()
        elif model == "TRG":
            self._trg()
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
        pv = self._vanilla(initSpot, noShares)
        return pv[0][0]
