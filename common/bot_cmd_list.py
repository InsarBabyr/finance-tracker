from aiogram.types import BotCommand

# Меню команд в личном чате с ботом (кнопка "Меню" рядом с полем ввода)
private = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="stats", description="Статистика за месяц"),
    BotCommand(command="undo", description="Отменить последний расход"),
]