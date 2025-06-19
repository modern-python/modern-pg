import typing

from sa_utils import helpers, is_dsn_multihost


def test_build_db_dsn() -> None:
    database_name: typing.Final = "new_db_name"
    drivername: typing.Final = "postgresql+asyncpg"
    result_dsn: typing.Final = helpers.build_db_dsn(
        db_dsn="postgresql://login:password@/db_placeholder?host=host1&host=host2",
        database_name=database_name,
        drivername=drivername,
    )

    assert database_name in result_dsn
    assert drivername in result_dsn


def test_is_dsn_multihost() -> None:
    assert is_dsn_multihost("postgresql://login:password@/db_placeholder?host=host1&host=host2")
    assert not is_dsn_multihost("postgresql://login:password@/db_placeholder?host=host1")
    assert not is_dsn_multihost("postgresql://login:password@host/db_placeholder")
