from abc import ABC, abstractmethod
from typing import Any, Callable
from notifier import Notifier
import psycopg2
import os


class ValueStore(ABC):

    @abstractmethod
    def update_value(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get_value(self, key: str) -> Any:
        pass


class PostgreSQLValueStore(ValueStore):

    def __init__(self, notifier: Notifier) -> None:
        self.__notifier = notifier
        self.__database_url = os.environ['DATABASE_URL']
        self.__create_table_if_not_exists()
        if not self.__key_exist('token'):
            initial_token = os.environ['INITIAL_TOKEN']
            self.update_value('token', initial_token)

    def __run_query(self, callable: Callable) -> Any:
        try:
            connection = psycopg2.connect(self.__database_url)
            cursor = connection.cursor()
            return callable(cursor, connection)
        except Exception as e:
            print(f"Unexpected database error: {e}")
            self.__notifier.notify_error(f"Unexpected database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def __create_table_if_not_exists(self) -> None:

        def query(cursor, connection) -> None:
            query = """
                CREATE TABLE IF NOT EXISTS config (
                    key VARCHAR UNIQUE NOT NULL,
                    value varchar,
                    PRIMARY KEY (key)
                );
            """
            cursor.execute(query)
            connection.commit()

        self.__run_query(query)

    def __key_exist(self, key: str) -> bool:

        def query(cursor, connection) -> Any:
            query = """
                SELECT *
                FROM config
                WHERE key = '%s';
            """ % key
            cursor.execute(query)
            return cursor.fetchone() is not None

        return self.__run_query(query)

    def update_value(self, key: str, value: Any) -> None:

        def query(cursor, connection) -> None:
            query = """
                INSERT INTO config (key, value)
                VALUES ('%s', '%s')
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value;
            """ % (key, value)
            cursor.execute(query)
            connection.commit()

        self.__run_query(query)

    def get_value(self, key: str) -> Any:

        def query(cursor, connection) -> Any:
            query = """
                SELECT *
                FROM config
                WHERE key = '%s';
            """ % key
            cursor.execute(query)
            return cursor.fetchone()[1]

        return self.__run_query(query)


class InMemoryValueStore(ValueStore):

    def __init__(self) -> None:
        self.__value_store = {}

    def update_value(self, key: str, value: Any) -> None:
        self.__value_store[key] = value

    def get_value(self, key: str) -> Any:
        return self.__value_store[key]
