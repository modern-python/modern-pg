import functools
import logging
import typing

import asyncpg
import tenacity
from sqlalchemy.exc import DBAPIError

from pg_tools import settings


P = typing.ParamSpec("P")
T = typing.TypeVar("T")
logger = logging.getLogger(__name__)


def _connection_retry_handler(exception: BaseException) -> bool:
    if (
        isinstance(exception, DBAPIError)
        and hasattr(exception, "orig")
        and isinstance(exception.orig.__cause__, asyncpg.PostgresConnectionError)  # type: ignore[union-attr]
    ):
        logger.debug("postgres_reconnect, backoff triggered")
        return True

    logger.debug("postgres_reconnect, giving up on backoff")
    return False


def postgres_reconnect(func: typing.Callable[P, typing.Awaitable[T]]) -> typing.Callable[P, typing.Awaitable[T]]:
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(settings.DB_UTILS_CONNECTION_TRIES),
        wait=tenacity.wait_exponential_jitter(),
        retry=tenacity.retry_if_exception(_connection_retry_handler),
        reraise=True,
        before=tenacity.before_log(logger, logging.DEBUG),
    )
    @functools.wraps(func)
    async def wrapped_method(*args: P.args, **kwargs: P.kwargs) -> T:
        return await func(*args, **kwargs)

    return wrapped_method


def _transaction_retry_handler(exception: BaseException) -> bool:
    if (
        isinstance(exception, DBAPIError)
        and hasattr(exception, "orig")
        and isinstance(exception.orig.__cause__, asyncpg.SerializationError)  # type: ignore[union-attr]
    ):
        logger.debug("transaction_retry, backoff triggered")
        return True

    logger.debug("transaction_retry, giving up on backoff")
    return False


def transaction_retry(
    func: typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]],
) -> typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]:
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(settings.DB_UTILS_TRANSACTIONS_TRIES),
        wait=tenacity.wait_exponential_jitter(),
        retry=tenacity.retry_if_exception(_transaction_retry_handler),
        reraise=True,
        before=tenacity.before_log(logger, logging.DEBUG),
    )
    @functools.wraps(func)
    async def wrapped_method(*args: P.args, **kwargs: P.kwargs) -> T:
        return await func(*args, **kwargs)

    return wrapped_method
