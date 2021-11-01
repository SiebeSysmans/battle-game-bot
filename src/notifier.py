from abc import ABC, abstractclassmethod
import telegram
import os


class Notifier(ABC):

    @abstractclassmethod
    def notify_info(self, text: str) -> None:
        pass

    @abstractclassmethod
    def notify_error(self, text: str) -> None:
        pass


class TelegramNotifier(Notifier):

    def __init__(self) -> None:
        self.__token = os.environ['TELEGRAM_TOKEN']
        self.__chat_id = os.environ['TELEGRAM_CHAT_ID']
        self.__telegram_bot = telegram.Bot(token=self.__token)

    def notify_info(self, text: str) -> None:
        self.__telegram_bot.send_message(
            text=text,
            chat_id=self.__chat_id,
            disable_notification=True
        )

    def notify_error(self, text: str) -> None:
        self.__telegram_bot.send_message(
            text=text,
            chat_id=self.__chat_id,
            disable_notification=False
        )


class MockNotifier(Notifier):

    def notify_info(self, text: str) -> None:
        print(f"Mock Notifier -- Info: {text}")

    def notify_error(self, text: str) -> None:
        print(f"Mock Notifier -- Error: {text}")


class EmptyNotifier(Notifier):

    def notify_info(self, text: str) -> None:
        pass

    def notify_error(self, text: str) -> None:
        pass
