from dataclasses import dataclass
from typing import List
import math


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

    def get_item_buy_structure_for_quantity(self, quantity: int) -> List:
        items: List = list(map(lambda unit_item: {
            "id": unit_item.id,
            "quantity": unit_item.quantity * quantity
        }, self.unit_items))
        return items

@dataclass
class Resources:
    citizens: int
    gold: int
