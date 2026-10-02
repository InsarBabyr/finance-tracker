import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Expense, User

# Часовой пояс для расчёта "текущего месяца". В БД время хранится в UTC.
# Астана сейчас живёт по UTC+5, в базе tz это Asia/Almaty.
TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "Asia/Almaty"))


# ---------- Пользователи ----------

async def orm_add_user(
    session: AsyncSession, user_id: int, username: str | None
) -> User:
    """Создаёт пользователя при первом обращении, при смене ника обновляет его."""
    user = await session.get(User, user_id)
    if user is None:
        user = User(user_id=user_id, username=username)
        session.add(user)
    elif user.username != username:
        user.username = username
    await session.commit()
    return user


# ---------- Расходы ----------

async def orm_add_expense(
    session: AsyncSession,
    user_id: int,
    amount: float,
    category: str,
    comment: str | None = None,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category,
        comment=comment,
    )
    session.add(expense)
    await session.commit()
    return expense


async def orm_get_last_expense(
    session: AsyncSession, user_id: int
) -> Expense | None:
    query = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.id.desc())
        .limit(1)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_delete_last_expense(
    session: AsyncSession, user_id: int
) -> Expense | None:
    """Удаляет последнюю запись пользователя (для /undo).

    Возвращает удалённый расход, чтобы показать его в ответе,
    или None, если записей нет.
    """
    expense = await orm_get_last_expense(session, user_id)
    if expense is None:
        return None
    await session.execute(delete(Expense).where(Expense.id == expense.id))
    await session.commit()
    return expense


# ---------- Статистика ----------

def _month_bounds_utc(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Границы текущего месяца в локальном часовом поясе, переведённые в UTC.

    Возвращает naive-datetime, так как в SQLite created_at хранится без tzinfo.
    """
    local_now = (now or datetime.now(timezone.utc)).astimezone(TIMEZONE)
    start_local = local_now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    if start_local.month == 12:
        end_local = start_local.replace(year=start_local.year + 1, month=1)
    else:
        end_local = start_local.replace(month=start_local.month + 1)

    to_utc = lambda dt: dt.astimezone(timezone.utc).replace(tzinfo=None)
    return to_utc(start_local), to_utc(end_local)


async def orm_get_month_stats(
    session: AsyncSession, user_id: int
) -> tuple[float, list[tuple[str, float]]]:
    """Итог за текущий месяц и суммы по категориям (от большей к меньшей).

    Возвращает (total, [(category, sum), ...]).
    """
    start, end = _month_bounds_utc()
    total_sum = func.sum(Expense.amount)

    query = (
        select(Expense.category, total_sum)
        .where(
            Expense.user_id == user_id,
            Expense.created_at >= start,
            Expense.created_at < end,
        )
        .group_by(Expense.category)
        .order_by(total_sum.desc())
    )
    result = await session.execute(query)
    rows = [(category, float(amount)) for category, amount in result.all()]
    total = sum(amount for _, amount in rows)
    return total, rows