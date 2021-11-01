from api import GraphQLAPI
from schedule import repeat, every, idle_seconds, run_pending
from dotenv import load_dotenv
from executor import SimpleActionExecutor
from runner import StrategyRunner
from value_store import PostgreSQLValueStore
from notifier import TelegramNotifier
import time
import math

load_dotenv()

notifier = TelegramNotifier()
value_store = PostgreSQLValueStore(notifier)
api = GraphQLAPI(value_store)
executor = SimpleActionExecutor(api)
runner = StrategyRunner(api, executor, notifier)


@repeat(every().hour.at("00:20"))
@repeat(every().hour.at("30:20"))
def main_job() -> None:
    try:
        runner.run_main_strategies()
    except Exception as e:
        print(f"Unexpected job error: {e}")
        notifier.notify_error(f"Unexpected job error: {e}")


def main() -> None:
    while True:
        time_to_sleep = idle_seconds()
        if time_to_sleep is None:
            break
        elif time_to_sleep > 0:
            print(f"Sleeping for {math.floor(time_to_sleep)} seconds...")
            time.sleep(time_to_sleep)
        run_pending()


if __name__ == "__main__":
    main()
