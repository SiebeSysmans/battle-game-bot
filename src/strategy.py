from action import (
    Action,
    BuyItemsAction,
    DepositGoldInTreasuryAction,
    TrainUnitAction,
    AttackPlayerAction
)
from models import Entities, Player, Resources
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import math


@dataclass
class StrategyPlan:
    actions: List[Action]
    adjusted_resources: Resources
    logs: List[str]


class Strategy(ABC):

    def __init__(self) -> None:
        self._actions: List[Action] = []
        self._adjusted_resources = Resources()
        self._logs: List[str] = []

    def plan(self, entities: Entities, resources: Resources, players: List[Player]) -> StrategyPlan:
        self._plan(entities, resources, players)
        return StrategyPlan(self._actions, self._adjusted_resources, self._logs)

    @abstractmethod
    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        pass


class SkipGoldStrategy(Strategy):

    def __init__(self, percentage: int) -> None:
        super().__init__()
        self.__percentage = percentage

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        gold_skip = math.floor(resources.gold * self.__percentage / 100)
        self._adjusted_resources.gold -= gold_skip
        self._logs.append(f"Skipping {self.__percentage}% ({gold_skip}) gold")


class SkipGoldRelativeToPlayersStrategy(Strategy):

    def __init__(self, percentage: int) -> None:
        super().__init__()
        self.__percentage = percentage

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:

        def player_gold_sort(player: Player):
            if player.gold is None:
                return 0
            else:
                return player.gold

        players.sort(key=player_gold_sort, reverse=True)
        highest_gold_player = players[0]
        gold_skip = min(
            math.floor(highest_gold_player.gold * self.__percentage / 100),
            resources.gold
        )
        self._adjusted_resources.gold -= gold_skip
        self._logs.append(
            f"Skipping {gold_skip} gold (highest was {highest_gold_player.username} with {highest_gold_player.gold} gold)")


class TrainMaxUnitStrategy(Strategy):

    def __init__(self, unit_name: str, with_items: bool = True) -> None:
        super().__init__()
        self.__unit_name = unit_name
        self.__with_items = with_items

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        if resources.citizens > 0:
            unit = next((unit for unit in entities.units
                         if unit.name == self.__unit_name), None)
            if unit is not None:
                if unit.has_items() and self.__with_items:
                    max_units = min(
                        math.floor(resources.gold / unit.total_item_price()),
                        resources.citizens
                    )
                    if max_units > 0:
                        self._adjusted_resources.gold -= unit.total_item_price() * max_units
                        self._actions.append(
                            BuyItemsAction(unit.get_item_buy_structure_for_quantity(max_units)))
                        self._logs.append(
                            f"Buying items for {max_units} {unit.name} units")
                        self._adjusted_resources.citizens -= max_units
                        self._actions.append(
                            TrainUnitAction(unit.id, max_units))
                        self._logs.append(
                            f"Training {max_units} {unit.name} units")
                else:
                    self._adjusted_resources.citizens -= resources.citizens
                    self._actions.append(
                        TrainUnitAction(unit.id, resources.citizens))
                    self._logs.append(
                        f"Training {resources.citizens} {unit.name} units")


class DepositMaxGoldInTreasuryStrategy(Strategy):

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        if resources.treasury_limit is None:
            max_deposit = resources.gold
        else:
            max_deposit = min(
                resources.treasury_limit - resources.treasury,
                resources.gold
            )
        if max_deposit > 0:
            self._adjusted_resources.gold -= max_deposit
            self._adjusted_resources.treasury += max_deposit
            self._actions.append(DepositGoldInTreasuryAction(max_deposit))
            self._logs.append(f"Depositing {max_deposit} gold in treasury")


class BuyMaxItemStrategy(Strategy):

    def __init__(self, item_name: str) -> None:
        super().__init__()
        self.__item_name = item_name

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        item = next((item for item in entities.items
                     if item.name == self.__item_name), None)
        if item is not None:
            max_items = math.floor(resources.gold / item.price)
            if max_items > 0:
                self._adjusted_resources.gold -= item.price * max_items
                self._actions.append(
                    BuyItemsAction([{"id": item.id, "quantity": max_items}]))
                self._logs.append(f"Buying {max_items} {item.name} items")


class BuyMaxItemsForUnitStrategy(Strategy):

    def __init__(self, unit_name: str) -> None:
        super().__init__()
        self.__unit_name = unit_name

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:
        unit = next((unit for unit in entities.units
                     if unit.name == self.__unit_name), None)
        if unit is not None:
            max_quantity = math.floor(resources.gold / unit.total_item_price())
            if max_quantity > 0:
                self._adjusted_resources.gold -= unit.total_item_price() * max_quantity
                self._actions.append(BuyItemsAction(
                    unit.get_item_buy_structure_for_quantity(max_quantity)))
                self._logs.append(
                    f"Buying items for {max_quantity} {unit.name} units")


class AttackHighestGoldPlayerStrategy(Strategy):

    def __init__(self, first: int) -> None:
        super().__init__()
        self.__first = first

    def _plan(self, entities: Entities, resources: Resources, players: List[Player]) -> None:

        def player_gold_sort(player: Player):
            if player.gold is None:
                return 0
            else:
                return player.gold

        players.sort(key=player_gold_sort, reverse=True)
        target = players[0]
        self._actions.append(AttackPlayerAction(target.id))
        self._logs.append(
            f"Attacking {target.username} with {target.gold} gold")
