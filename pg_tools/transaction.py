import dataclasses

import typing_extensions
from sqlalchemy.ext import asyncio as sa_async


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class Transaction:
    session: sa_async.AsyncSession

    async def __aenter__(self) -> typing_extensions.Self:
        await self.session.begin()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()
