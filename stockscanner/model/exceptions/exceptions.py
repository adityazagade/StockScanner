class StrategyNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AssetNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PortfolioCreationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
