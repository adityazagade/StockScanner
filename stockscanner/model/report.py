import matplotlib.pyplot as plt
from math import log


class Report:
    def __init__(self, p=None) -> None:
        self.p = p
        self.__performance = []

    def __str__(self) -> str:
        plt.scatter(*zip(*self.__performance))
        plt.show()
        res = f"{self.p}"
        return res

    def add_portfolio(self, p):
        self.p = p

    def track(self, entry):
        self.__performance.append(entry)
