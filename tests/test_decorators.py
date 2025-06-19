import pytest
import sqlalchemy
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext import asyncio as sa_async

from modern_pg.decorators import postgres_reconnect, transaction_retry


@pytest.mark.parametrize(
    "error_code",
    [
        "40001",  # SerializationError - backoff triggered
        "40002",  # StatementCompletionUnknownError - backoff not triggered
    ],
)
async def test_transaction_retry(async_engine: sa_async.AsyncEngine, error_code: str) -> None:
    async with async_engine.connect() as connection:
        await connection.execute(
            sqlalchemy.text(
                f"""
        CREATE OR REPLACE FUNCTION raise_error()
        RETURNS VOID AS $$
        BEGIN
            RAISE SQLSTATE '{error_code}';
        END;
        $$ LANGUAGE plpgsql;
        """,
            ),
        )

        @transaction_retry
        async def raise_error() -> None:
            await connection.execute(sqlalchemy.text("SELECT raise_error()"))

        with pytest.raises(DBAPIError):
            await raise_error()


@pytest.mark.parametrize(
    "error_code",
    [
        "08000",  # PostgresConnectionError - backoff triggered
        "08003",  # subclass of PostgresConnectionError - backoff triggered
        "03000",  # backoff not triggered
    ],
)
async def test_postgres_reconnect(async_engine: sa_async.AsyncEngine, error_code: str) -> None:
    async with async_engine.connect() as connection:
        await connection.execute(
            sqlalchemy.text(
                f"""
        CREATE OR REPLACE FUNCTION raise_error()
        RETURNS VOID AS $$
        BEGIN
            RAISE SQLSTATE '{error_code}';
        END;
        $$ LANGUAGE plpgsql;
        """,
            ),
        )

        @postgres_reconnect
        async def other_error() -> None:
            await connection.execute(sqlalchemy.text("SELECT raise_error()"))

        with pytest.raises(DBAPIError):
            await other_error()
