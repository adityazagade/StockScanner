class Report:
    def __init__(self, p=None) -> None:
        self.p = p
        self.performance = []

    def __str__(self) -> str:
        res = f"{self.p}"
        return res

    def add_portfolio(self, p):
        self.p = p

    def track(self, entry):
        self.performance.append(entry)
