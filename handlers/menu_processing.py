from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_delete_last_expense, orm_get_month_stats
from kbds.reply import BTN_ADD, BTN_STATS, BTN_UNDO
from utils.formatter import format_deleted, format_stats

# Этот роутер в app.py подключается ПЕРВЫМ, чтобы нажатия на кнопки меню
# не попадали в обработчик свободного текста из user_private.py
menu_router = Router()


@menu_router.message(F.text == BTN_ADD)
async def add_button(message: Message) -> None:
    await message.answer(
        "Отправьте сумму:\n"
        "• <code>2500</code> — выберете категорию кнопками\n"
        "• <code>1500 Такси</code> — запишу сразу"
    )


@menu_router.message(Command("stats"))
@menu_router.message(F.text == BTN_STATS)
async def stats(message: Message, session: AsyncSession) -> None:
    total, rows = await orm_get_month_stats(session, message.from_user.id)
    await message.answer(format_stats(total, rows))


@menu_router.message(Command("undo"))
@menu_router.message(F.text == BTN_UNDO)
async def undo(message: Message, session: AsyncSession) -> None:
    deleted = await orm_delete_last_expense(session, message.from_user.id)
    if deleted is None:
        await message.answer("Нечего отменять: записей пока нет.")
        return
    await message.answer(format_deleted(deleted))