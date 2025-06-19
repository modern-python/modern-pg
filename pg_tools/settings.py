import os
import typing


DB_UTILS_CONNECTION_TRIES: typing.Final = int(os.getenv("DB_UTILS_CONNECTION_TRIES", "3"))
DB_UTILS_TRANSACTIONS_TRIES: typing.Final = int(os.getenv("DB_UTILS_TRANSACTIONS_TRIES", "3"))
