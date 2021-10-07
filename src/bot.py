from typing import List
from api import API
from models import Unit
from notifier import Notifier
import math


class Bot:

    def __init__(self, api: API, notifier: Notifier) -> None:
        self.__api = api
        self.__notifier = notifier

    def train_units(self, name: str) -> None:
        # Refresh token
        new_token = self.__api.refresh_token()
        print(f"New token: {new_token}")

        # Get resources
        units = self.__api.get_units()
        resources = self.__api.get_profile_resources()
        citizen_price = self.__api.get_citizen_prize()

        # Plan
        unit = self.__find_unit(units, name)
        unit_total_price = unit.total_item_price()
        total_citizen_price = resources.citizens * unit_total_price
        new_citizen_price = citizen_price + unit_total_price
        netto_gold = resources.gold - total_citizen_price
        citizens_to_recruit = (netto_gold - (netto_gold %
                               new_citizen_price)) / new_citizen_price
        trainable_citizens = citizens_to_recruit + resources.citizens

        # Execute
        rapport = "----------"
        if trainable_citizens > 0:
            if citizens_to_recruit > 0:
                self.__api.recruit_citizen(citizens_to_recruit)
            self.__api.buy_items(
                unit.get_item_buy_structure_for_quantity(trainable_citizens))
            self.__api.train_unit(unit.id, trainable_citizens)
            rapport += f"\nTrained {trainable_citizens} {unit.name} units"
        else:
            rapport += "\nNo units to train"
        rapport += "\n----------"
        rapport += "\nJob ran succesfully!"
        print(rapport)
        self.__notifier.notify_info(rapport)

    def convert_units(self, from_name: str, to_names: List[str]) -> None:
        # Refresh token
        new_token = self.__api.refresh_token()
        print(f"New token: {new_token}")

        # Get resources
        units = self.__api.get_units()
        resources = self.__api.get_profile_resources()

        # Plan
        from_unit = self.__find_unit(units, from_name)
        to_units = list(
            map(lambda to_name: self.__find_unit(units, to_name), to_names))
        total_cost = sum(
            int(to_unit.total_item_price())
            for to_unit in to_units
        )
        total_to_train = sum(
            int(to_unit.units_per_job())
            for to_unit in to_units
        )
        quantity_to_buy = math.floor(resources.gold / total_cost)
        total_to_untrain = total_to_train - resources.citizens

        # Execute
        rapport = "----------"
        if total_to_untrain > 0:
            self.__api.untrain_unit(from_unit.id, total_to_untrain)
            rapport += f"\nUntrained {total_to_untrain} {from_unit.name} units"
        for to_unit in to_units:
            if quantity_to_buy > 0:
                self.__api.buy_items(
                    to_unit.get_item_buy_structure_for_quantity(quantity_to_buy))
                rapport += f"\nBought {quantity_to_buy} items for {to_unit.name}"
            self.__api.train_unit(to_unit.id, to_unit.units_per_job())
            rapport += f"\nTrained {to_unit.units_per_job()} {to_unit.name} units"
        rapport += "\n----------"
        rapport += "\nJob ran succesfully!"
        print(rapport)
        self.__notifier.notify_info(rapport)

    def __find_unit(self, units: List[Unit], name: str) -> Unit:
        return next(unit for unit in units if unit.name == name)
