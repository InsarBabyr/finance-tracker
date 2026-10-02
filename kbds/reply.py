from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Тексты кнопок вынесены в константы: по ним хендлеры ловят нажатия
BTN_ADD = "➕ Добавить расход"
BTN_STATS = "📊 Статистика"
BTN_UNDO = "↩️ Отменить последнее"


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Главное меню (Reply Keyboard) из ТЗ."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADD)],
            [KeyboardButton(text=BTN_STATS), KeyboardButton(text=BTN_UNDO)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Например: 1500 Такси",
    )