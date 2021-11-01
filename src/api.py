from typing import List, Dict
from models import (
    BattleResult,
    Entities,
    Item,
    Player,
    Resources,
    Unit,
    UnitItem
)
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from abc import ABC, abstractmethod
from value_store import ValueStore
import os


class API(ABC):

    @abstractmethod
    def refresh_token(self) -> str:
        pass

    @abstractmethod
    def get_citizen_prize(self) -> int:
        pass

    @abstractmethod
    def get_profile_resources(self) -> Resources:
        pass

    @abstractmethod
    def recruit_citizen(self, amount: int) -> None:
        pass

    @abstractmethod
    def train_unit(self, unit_id: int, quantity: int) -> None:
        pass

    @abstractmethod
    def untrain_unit(self, unit_id: int, quantity: int) -> None:
        pass

    @abstractmethod
    def buy_items(self, items: List[Dict[str, int]]) -> None:
        pass

    @abstractmethod
    def get_entities(self) -> Entities:
        pass

    @abstractmethod
    def deposit_to_treasury(self, amount: int) -> None:
        pass

    @abstractmethod
    def get_players(self, first: int) -> List[Player]:
        pass

    @abstractmethod
    def attack_player(self, id: int) -> BattleResult:
        pass


class GraphQLAPI(API):

    def __init__(self, value_store: ValueStore) -> None:
        self.__value_store = value_store
        self.__transport = AIOHTTPTransport(
            url=os.environ['API_ENDPOINT'],
            headers={
                "authorization": f"Bearer {value_store.get_value('token')}",
                "User-Agent": "okhttp/3.12.12",
                "Content-Type": "application/json"
            }
        )
        self.__client = Client(transport=self.__transport)

    def refresh_token(self) -> str:

        def map(response) -> str:
            token = response["refreshToken"]
            return token

        query = gql(
            """
                mutation {
                    refreshToken
                }
            """
        )
        response = self.__client.execute(query)
        token = map(response)
        self.__value_store.update_value('token', token)
        self.__transport.headers = {
            "authorization": f"Bearer {token}",
        }
        return token

    def get_citizen_prize(self) -> int:

        def map(response) -> int:
            price = response["recruitCitizenPrice"]
            return price

        query = gql(
            """
                query {
                    recruitCitizenPrice
                }
            """
        )
        response = self.__client.execute(query)
        return map(response)

    def get_profile_resources(self) -> Resources:

        def map(response) -> Resources:
            resources = Resources(
                response["viewerProfile"]["housing"]["citizens"],
                response["viewerProfile"]["resources"]["gold"],
                response["viewerProfile"]["resources"]["treasury"],
                response["viewerProfile"]["upgrades"]["treasury"]["current"]["limit"]
            )
            return resources

        query = gql(
            """
                query {
                    viewerProfile {
                        housing {
                            citizens
                        }
                        resources {
                            gold
                            treasury
                        }
                        upgrades {
                            treasury {
                                current {
                                    limit
                                }
                            }
                        }
                    }
                }
            """
        )
        response = self.__client.execute(query)
        return map(response)

    def recruit_citizen(self, amount: int) -> None:
        query = gql(
            """
                mutation ($input: ActionRecruitCitizens!) {
                    actionRecruitCitizens(input: $input) {
                        citizens
                        max_citizens
                    }
                }
            """
        )
        variables = {
            "input": {
                "amount": amount
            }
        }
        self.__client.execute(query, variable_values=variables)

    def train_unit(self, unit_id: int, quantity: int) -> None:
        query = gql(
            """
                mutation ($input: ActionTrainUnitInput!) {
                    actionTrainBuildingUnit(input: $input) {
                        id
                    }
                }
            """
        )
        variables = {
            "input": {
                "id": unit_id,
                "quantity": quantity
            }
        }
        self.__client.execute(query, variable_values=variables)

    def untrain_unit(self, unit_id: int, quantity: int) -> None:
        query = gql(
            """
                mutation ($input: ActionUntrainUnitInput!) {
                    actionUntrainBuildingUnit(input: $input) {
                        id
                    }
                }
            """
        )
        variables = {
            "input": {
                "id": unit_id,
                "quantity": quantity
            }
        }
        self.__client.execute(query, variable_values=variables)

    def buy_items(self, items: List[Dict[str, int]]) -> None:
        query = gql(
            """
                mutation ($input: ActionBuyItemsInput!) {
                    actionBuyItems(input: $input) {
                        owned_items {
                            item {
                                id
                                name
                            }
                            quantity
                        }
                    }
                }
            """
        )
        variables = {
            "input": {
                "items": items
            }
        }
        self.__client.execute(query, variable_values=variables)

    def get_entities(self) -> Entities:

        def map(response) -> Entities:
            units: List[Unit] = []
            items: List[Item] = []
            response_buildings = response["buildings"]["data"]
            for response_building in response_buildings:
                response_units = response_building["units"]
                for response_unit in response_units:
                    unit_items: List[UnitItem] = []
                    response_items = response_unit["unit_items"]
                    for response_item in response_items:
                        unit_item = UnitItem(
                            response_item["item"]["id"],
                            response_item["item"]["name"],
                            response_item["item"]["price"],
                            response_item["quantity"]
                        )
                        unit_items.append(unit_item)
                    unit = Unit(
                        response_unit["id"],
                        response_unit["name"],
                        response_unit["training_time"]["totalSeconds"],
                        unit_items
                    )
                    units.append(unit)
                response_items = response_building["items"]
                for response_item in response_items:
                    item = Item(
                        response_item["id"],
                        response_item["name"],
                        response_item["price"]
                    )
                    items.append(item)
            return Entities(units, items)

        query = gql(
            """
                query {
                buildings {
                    data {
                        name
                        main_type
                        units {
                            ...Unit
                        }
                        items {
                            ...Item
                        }
                    }
                }
                }

                fragment Unit on Unit {
                    id
                    name
                    attack_strength
                    defense_strength
                    gold_proceeds
                    training_time {
                        totalSeconds
                    }
                    is_available
                    unit_items {
                        item {
                        ...Item
                        }
                        quantity
                    }
                }

                fragment Item on Item {
                    id
                    name
                    price
                }
            """
        )
        response = self.__client.execute(query)
        return map(response)

    def deposit_to_treasury(self, amount: int) -> None:
        query = gql(
            """
                mutation ($input: ActionTreasuryTransferInput!) {
                    actionTreasuryDeposit(input: $input) {
                        id
                    }
                }
            """
        )
        variables = {
            "input": {
                "amount": amount
            }
        }
        self.__client.execute(query, variable_values=variables)

    def get_players(self, first: int) -> List[Player]:

        def map(response) -> List[Player]:
            response_players = response["profiles"]["data"]
            players: List = []
            for response_player in response_players:
                players.append(
                    Player(
                        response_player["id"],
                        response_player["username"],
                        response_player["resources"]["gold"]
                    )
                )
            return players

        query = gql(
            """
                query ($first: Int!) {
                    profiles(first: $first) {
                        data {
                            id
                            username
                            resources {
                                gold
                            }
                        }
                    }
                }
            """
        )
        variables = {
            "first": first
        }
        response = self.__client.execute(query, variable_values=variables)
        return map(response)

    def attack_player(self, id: int) -> BattleResult:

        def map(response) -> BattleResult:
            result = response["actionBattle"]["result"]
            gold_stolen = response["actionBattle"]["gold_stolen"]
            return BattleResult(result, gold_stolen)

        query = gql(
            """
                mutation($input: ActionBattleInput!) {
                    actionBattle(input: $input) {
                        result
                        gold_stolen
                    }
                }
            """
        )
        variables = {
            "input": {
                "id": id
            }
        }
        response = self.__client.execute(query, variable_values=variables)
        return map(response)


class MockAPI(ABC):

    def refresh_token(self) -> str:
        print(f"Mock API -- Refreshing token...")
        return "NEW_TOKEN"

    def get_citizen_prize(self) -> int:
        print(f"Mock API -- Getting citizen prize...")
        return 100_000

    def get_profile_resources(self) -> Resources:
        print(f"Mock API -- Getting profile resources...")
        return Resources(5, 100_000, 80_000, 100_000)

    def recruit_citizen(self, amount: int) -> None:
        print(f"Mock API -- Recruiting {amount} citizens...")

    def train_unit(self, unit_id: int, quantity: int) -> None:
        print(
            f"Mock API -- Training {quantity} units with ID = {unit_id}...")

    def untrain_unit(self, unit_id: int, quantity: int) -> None:
        print(
            f"Mock API -- Untraining {quantity} units with ID = {unit_id}...")

    def buy_items(self, items: List[Dict[str, int]]) -> None:
        print(f"Mock API -- Buying items... {items}")

    def get_entities(self) -> Entities:
        print(f"Mock API -- Getting units...")
        units: List[Unit] = [
            Unit(0, "Unit 0", 10, [
                UnitItem(0, "Item 0", 1_000, 1),
                UnitItem(1, "Item 1", 2_000, 2)
            ]),
            Unit(1, "Unit 1", 20, [
                UnitItem(2, "Item 2", 3_000, 1)
            ]),
            Unit(2, "Unit 2", 40, [
                UnitItem(0, "Item 0", 1_000, 1)
            ]),
            Unit(3, "Unit 3", 30, [])
        ]
        items: List[Item] = [
            Item(0, "Item 0", 1_000),
            Item(1, "Item 1", 2_000),
            Item(2, "Item 2", 3_000)
        ]
        return Entities(units, items)

    def deposit_to_treasury(self, amount: int) -> None:
        print(f"Mock API -- Depositing {amount} gold to treasury...")

    def get_players(self, first: int) -> List[Player]:
        print(f"Mock API -- Getting players...")
        players: List[Player] = [
            Player(0, "Player 0", 100_000),
            Player(1, "Player 1", 200_000),
            Player(2, "Player 2", None)
        ]
        return players

    def attack_player(self, id: int) -> BattleResult:
        print(f"Mock API -- Attack player with id {id}...")
        return BattleResult("Success", 50_000)
