from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict
from api import API


class Action(ABC):

    @abstractmethod
    def execute(self, api: API) -> None:
        pass


@dataclass
class TrainUnitAction(Action):
    unit_id: int
    quantity: int

    def execute(self, api: API) -> None:
        api.train_unit(self.unit_id, self.quantity)


@dataclass
class UntrainUnitAction(Action):
    unit_id: int
    quantity: int

    def execute(self, api: API) -> None:
        api.untrain_unit(self.unit_id, self.quantity)


@dataclass
class DepositGoldInTreasuryAction(Action):
    amount: int

    def execute(self, api: API) -> None:
        api.deposit_to_treasury(self.amount)


@dataclass
class BuyItemsAction(Action):
    items: List[Dict[str, int]]

    def execute(self, api: API) -> None:
        api.buy_items(self.items)


@dataclass
class AttackPlayerAction(Action):
    id: int

    def execute(self, api: API) -> None:
        api.attack_player(self.id)
