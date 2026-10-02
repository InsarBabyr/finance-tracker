import os

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models import Base

# По умолчанию файл БД лежит рядом с app.py. Можно переопределить в .env:
# DB_URL=sqlite+aiosqlite:///my_base.db
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///my_base.db")

engine = create_async_engine(DB_URL, echo=False)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    # В SQLite внешние ключи по умолчанию выключены, включаем их для каждого соединения
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# expire_on_commit=False, чтобы объекты оставались доступными после commit()
session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db() -> None:
    """Создаёт таблицы, если их ещё нет. Существующие данные не затрагивает."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Удаляет все таблицы. Только для разработки, в app.py не вызывается."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)