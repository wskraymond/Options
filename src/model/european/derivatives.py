import math
from abc import ABC, abstractmethod

import numpy as np


class PrecisionError(Exception):
    def __init__(self, args):
        super().__init__(args)


class Derivatives(ABC):
    def __init__(self, name, tenor, n):
        self.name = name
        self.tenor = tenor
        self.n = n
        if self.n is not None:
            self.h = self.tenor / self.n

    def compare_float(self, a, b, epsilon=1e-9):
        if self.h ** 2 < epsilon:
            raise PrecisionError("epsilon is not smaller enough than input parameter for pricing", self.h ** 2)

        if math.isclose(a, b, abs_tol=epsilon):
            return 0
        elif a > b:
            return 1
        else:
            return -1

    def is_all_float_ge(self, a, b, epsilon=1e-9):
        if self.h ** 2 < epsilon:
            raise PrecisionError("epsilon is not smaller enough than input parameter for pricing", self.h ** 2)

        return np.allclose(a, b, atol=epsilon) | (a > b)

    def is_all_float_le(self, a, b, epsilon=1e-9):
        if self.h ** 2 < epsilon:
            raise PrecisionError("epsilon is not smaller enough than input parameter for pricing", self.h ** 2)

        return np.allclose(a, b, atol=epsilon) | (a < b)

    @abstractmethod
    def price(self, initSpot, noShares):
        pass
