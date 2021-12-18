from datetime import date

from stockscanner.model.asset.asset import Asset
from stockscanner.model.asset.asset_type import AssetType


class Cash(Asset):
    def add_by_amount(self, amount: float, d: date = date.today()):
        self.add(amount=amount)

    def reduce_by_amount(self, amount: float, d: date = date.today()):
        self.remove(amount=amount)

    def __init__(self, amount: float) -> None:
        super().__init__()
        self.type = AssetType.CASH
        self.amount = amount

    def remove(self, **kwargs):
        if self.amount < kwargs.get("amount"):
            raise Exception("Cannot remove more amount than what you have")
        self.amount -= kwargs.get("amount")

    def get_current_value(self) -> float:
        return self.amount

    def get_value_as_of_date(self, d: date):
        return self.amount

    def add(self, **kwargs):
        self.amount += kwargs.get("amount")

    def get_invested_amount(self) -> float:
        return self.amount

    def get_trade_book(self):
        return []