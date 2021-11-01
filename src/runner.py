from strategy import (
    Strategy,
    SkipGoldRelativeToPlayersStrategy,
    DepositMaxGoldInTreasuryStrategy,
    TrainMaxUnitStrategy
)
from typing import List
from action import Action
from executor import SimpleActionExecutor
from notifier import Notifier
from api import API
import random


class StrategyRunner:

    def __init__(self, api: API, executor: SimpleActionExecutor, notifier: Notifier) -> None:
        self.__api = api
        self.__executor = executor
        self.__notifier = notifier

    def __run_strategies(self, strategies: List[Strategy]) -> None:
        # Get resources
        entities = self.__api.get_entities()
        resources = self.__api.get_profile_resources()
        players = self.__api.get_players(50)

        # Build actions
        actions: List[Action] = []
        logs: List[str] = []

        for strategy in strategies:
            strategy_plan = strategy.plan(entities, resources, players)
            actions.extend(strategy_plan.actions)
            resources.adjust(
                strategy_plan.adjusted_resources.citizens,
                strategy_plan.adjusted_resources.gold,
                strategy_plan.adjusted_resources.treasury
            )
            logs.extend(strategy_plan.logs)

        # Execute
        self.__executor.execute(actions)

        # Report
        rapport = ""
        for log in logs:
            rapport += log
            rapport += "\n"
        rapport += f"Job ran successfully!"
        print(rapport)
        self.__notifier.notify_info(rapport)

    def run_main_strategies(self) -> None:
        # Refresh token
        new_token = self.__api.refresh_token()
        print(f"New token: {new_token}")

        # Plan
        strategies: List[Strategy] = [
            SkipGoldRelativeToPlayersStrategy(50),
            TrainMaxUnitStrategy("Slinger"),
            DepositMaxGoldInTreasuryStrategy()
        ]

        self.__run_strategies(strategies)
