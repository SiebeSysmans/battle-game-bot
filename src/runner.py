from api import GraphQLAPI
from bot import Bot
from schedule import repeat, every, idle_seconds, run_pending
from dotenv import load_dotenv
from value_store import PostgreSQLValueStore
from notifier import TelegramNotifier
import time

load_dotenv()

notifier = TelegramNotifier()
value_store = PostgreSQLValueStore(notifier)
api = GraphQLAPI(value_store)
bot = Bot(api, notifier)


@repeat(every().hour.at("00:20"))
@repeat(every().hour.at("30:20"))
def auto_convert_units_job() -> None:
    try:
        bot.convert_units(
            from_name="Slinger",
            to_names=["Sword Fighter", "Crossbowman"]
        )
    except Exception as e:
        print(f"Unexpected job error: {e}")
        notifier.notify_error(f"Unexpected job error: {e}")


def main() -> None:
    while True:
        time_to_sleep = idle_seconds()
        if time_to_sleep is None:
            break
        elif time_to_sleep > 0:
            print(f"Sleeping for {time_to_sleep} seconds...")
            time.sleep(time_to_sleep)
        run_pending()


if __name__ == "__main__":
    main()
