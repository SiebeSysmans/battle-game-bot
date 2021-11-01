from abc import ABC, abstractmethod
from typing import List
from action import Action
from api import API


class ActionExecutor(ABC):

    @abstractmethod
    def execute(self, actions: List[Action]) -> None:
        pass


class SimpleActionExecutor(ActionExecutor):

    def __init__(self, api: API) -> None:
        self.__api = api

    def execute(self, actions: List[Action]) -> None:
        for action in actions:
            action.execute(self.__api)
