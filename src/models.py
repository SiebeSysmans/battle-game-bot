from dataclasses import dataclass
from typing import List
import math


@dataclass
class Item:
    id: int
    name: str
    price: int


@dataclass
class UnitItem:
    id: int
    name: str
    price: int
    quantity: int


@dataclass
class Unit:
    id: int
    name: str
    training_time: int
    unit_items: List[UnitItem]

    def total_item_price(self) -> int:
        total_price = sum(
            int(unit_item.price * unit_item.quantity)
            for unit_item in self.unit_items
        )
        return total_price

    def units_per_job(self) -> int:
        return math.floor(1800 / self.training_time)

    def has_items(self) -> bool:
        return self.unit_items is not None and len(self.unit_items) != 0

    def get_item_buy_structure_for_quantity(self, quantity: int) -> List:
        items: List = list(map(lambda unit_item: {
            "id": unit_item.id,
            "quantity": unit_item.quantity * quantity
        }, self.unit_items))
        return items


@dataclass
class Player:
    id: int
    username: str
    gold: int


@dataclass
class BattleResult:
    result: str
    gold_stolen: int


@dataclass
class Entities:
    units: List[Unit]
    items: List[Item]


@dataclass
class Resources:
    citizens: int = 0
    gold: int = 0
    treasury: int = 0
    treasury_limit: int = 0

    def adjust(self, citizens: int, gold: int, treasury: int):
        self.citizens += citizens
        self.gold += gold
        self.treasury += treasury
