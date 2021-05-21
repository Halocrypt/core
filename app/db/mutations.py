from typing import Any
from sqlalchemy.ext.asyncio.session import AsyncSession


async def add_to_db(db: AsyncSession, row: Any):
    db.add(row)
    await db.commit()


async def delete_from_db(db: AsyncSession, row: Any):
    await db.delete(row)
    await db.commit()
