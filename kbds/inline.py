from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.categories import CATEGORIES


class CategoryCallback(CallbackData, prefix="cat"):
    """Нажатие на категорию. Сумма хранится прямо в кнопке,
    поэтому бот не теряет её даже после перезапуска."""

    key: str
    amount: float


class CancelCallback(CallbackData, prefix="cancel"):
    """Отмена выбора категории (расход не сохраняется)."""


def categories_kb(amount: float) -> InlineKeyboardMarkup:
    """Inline-клавиатура с категориями для варианта Б ("2500" -> выбор категории)."""
    builder = InlineKeyboardBuilder()

    for category in CATEGORIES:
        builder.button(
            text=category.title,
            callback_data=CategoryCallback(key=category.key, amount=amount),
        )
    builder.adjust(2)  # две кнопки в ряд

    # Кнопка отмены отдельной строкой внизу
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=CancelCallback().pack(),
        )
    )
    return builder.as_markup()