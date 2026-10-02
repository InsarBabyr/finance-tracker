import re
from dataclasses import dataclass

from common.categories import (
    CATEGORY_BY_NAME,
    DEFAULT_CATEGORY,
    Category,
    match_category,
)

# Сумма: "1500", "1 200" (пробел или неразрывный пробел между тысячами),
# дробная часть через точку или запятую: "1 200,50", "99.9".
# Остаток строки - категория/комментарий.
_EXPENSE_RE = re.compile(
    r"""^\s*
    (?P<int>\d{1,3}(?:[ \u00a0]\d{3})+|\d+)   # целая часть
    (?:[.,](?P<frac>\d{1,2}))?                # дробная часть
    (?:\s+|$)                                 # пробел после суммы или конец строки
    (?P<rest>.*?)\s*$
    """,
    re.VERBOSE | re.DOTALL,
)

MAX_AMOUNT = 100_000_000


@dataclass(frozen=True)
class ParsedExpense:
    amount: float
    category: Category | None  # None -> сумма без текста, нужно спросить кнопками
    comment: str | None


def parse_expense(text: str) -> ParsedExpense | None:
    """Разбирает сообщение вида "<сумма> <категория/комментарий>".

    Примеры:
        "1500 Такси"      -> 1500, Транспорт, "Такси"
        "2500"            -> 2500, category=None (бот покажет кнопки)
        "1 200,50 кофе"   -> 1200.5, Кафе и Рестораны, "кофе"
        "700 что-то там"  -> 700, Другое, "что-то там"
        "привет"          -> None (это не расход)
    """
    match = _EXPENSE_RE.match(text or "")
    if match is None:
        return None

    int_part = re.sub(r"[ \u00a0]", "", match["int"])
    amount = float(f"{int_part}.{match['frac'] or '0'}")
    if not 0 < amount <= MAX_AMOUNT:
        return None

    rest = match["rest"].strip()
    if not rest:
        return ParsedExpense(amount=amount, category=None, comment=None)

    category = match_category(rest) or DEFAULT_CATEGORY

    # Если пользователь написал просто название категории ("500 Транспорт"),
    # комментарий не нужен
    comment = None if rest.lower() in CATEGORY_BY_NAME else rest

    return ParsedExpense(amount=amount, category=category, comment=comment)