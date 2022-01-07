import math
import numpy as np
from scripts.european.derivatives import *


def CRR_method(K, T, S0, r, N, sigma, opttype='C'):
    # precomute constants
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    q = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    # initialise asset prices at maturity - Time step N
    S = np.zeros(N + 1)
    S[0] = S0 * d ** N
    for j in range(1, N + 1):
        S[j] = S[j - 1] * u / d

    # initialise option values at maturity
    C = np.zeros(N + 1)
    for j in range(0, N + 1):
        if opttype == 'C':
            C[j] = max(0, S[j] - K)
        else:
            C[j] = max(0, K - S[j])

    # step backwards through tree
    for i in np.arange(N, 0, -1):
        for j in range(0, i):
            C[j] = disc * (q * C[j + 1] + (1 - q) * C[j])

    return C[0]

def TRG_method(K, T, S0, r, N, sigma, opttype='C'):
    # precomute constants
    dt = T / N
    nu = r - 0.5 * sigma ** 2
    dxu = np.sqrt(sigma ** 2 * dt + nu ** 2 * dt ** 2)
    dxd = -dxu
    pu = 0.5 + 0.5 * nu * dt / dxu
    pd = 1 - pu
    disc = np.exp(-r * dt)

    # initialise asset prices at maturity - Time step N
    S = np.zeros(N + 1)
    S[0] = S0 * np.exp(N * dxd)
    for j in range(1, N + 1):
        S[j] = S[j - 1] * np.exp(dxu - dxd)

    # initialise option values at maturity
    C = np.zeros(N + 1)
    for j in range(0, N + 1):
        if opttype == 'C':
            C[j] = max(0, S[j] - K)
        else:
            C[j] = max(0, K - S[j])

    # step backwards through tree
    for i in np.arange(N, 0, -1):
        for j in range(0, i):
            C[j] = disc * (pu * C[j + 1] + pd * C[j])

    return C[0]

class Vanilla(Derivatives):
    style = "European"

    def __init__(self, name, r, std, tenor, n, strike, opt):
        self.name = name
        self.tenor = tenor
        self.n = n
        self.h = self.tenor / self.n
        self.r = r
        self.df = np.exp(-self.h * self.r)
        self.std = std
        self.u = np.exp(np.sqrt(self.h) * self.std)
        self.d = 1.0 / self.u
        self.p = (1.0 / self.df - self.d) / (self.u - self.d)
        self.strike = strike
        self.opt = opt

        # PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]
        self._f = lambda pvUp, pvDown: \
            self.df * (self.p * pvUp + (1.0 - self.p) * pvDown)

        # s(i,j) = s0 * u^j * d^i-j
        self.s = lambda initSpot, totalDown, noUp: \
            initSpot * self.u ** np.sqrt(noUp) * self.d ** np.sqrt(totalDown - noUp)

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

        # Vanilla price
        for i in reversed(range(self.n)):
            for j in range(i + 1):
                pv[i][j] = self._f(pvUp=pv[i + 1][j + 1], pvDown=pv[i + 1][j])

        return pv

    def price(self, initSpot, noShares=100):
        pv = self._vanilla(initSpot, noShares)
        return pv[0][0]
