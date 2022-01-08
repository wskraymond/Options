from abc import ABC, abstractmethod


class Derivatives(ABC):
    @abstractmethod
    def price(self, initSpot, noShares):
        pass
