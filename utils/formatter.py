from datetime import datetime
from html import escape

from common.categories import title_by_name
from database.models import Expense
from database.orm_query import TIMEZONE

CURRENCY = "₸"

_MONTHS = (
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
)


def format_amount(amount: float) -> str:
    """1500 -> "1 500 ₸", 1200.5 -> "1 200,50 ₸"."""
    if float(amount).is_integer():
        text = f"{int(amount):,}".replace(",", "\u00a0")
    else:
        text = f"{amount:,.2f}".replace(",", "\u00a0").replace(".", ",")
    return f"{text}\u00a0{CURRENCY}"


def _expense_lines(expense: Expense) -> str:
    line = f"{format_amount(expense.amount)} — {title_by_name(expense.category)}"
    if expense.comment:
        # Текст приходит от пользователя, экранируем, т.к. бот работает в режиме HTML
        line += f"\n💬 {escape(expense.comment)}"
    return line


def format_added(expense: Expense) -> str:
    return f"✅ Записано:\n{_expense_lines(expense)}"


def format_deleted(expense: Expense) -> str:
    return f"↩️ Удалено:\n{_expense_lines(expense)}"


def format_stats(total: float, rows: list[tuple[str, float]]) -> str:
    """Итог за текущий месяц и распределение по категориям."""
    now = datetime.now(TIMEZONE)
    title = f"📊 <b>Статистика: {_MONTHS[now.month - 1]} {now.year}</b>"

    if not rows:
        return f"{title}\n\nВ этом месяце расходов пока нет."

    lines = [title, "", f"Всего потрачено: <b>{format_amount(total)}</b>", ""]
    for category, amount in rows:
        percent = round(amount / total * 100) if total else 0
        lines.append(
            f"{title_by_name(category)} — {format_amount(amount)} ({percent}%)"
        )
    return "\n".join(lines)