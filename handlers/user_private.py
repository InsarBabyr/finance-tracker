from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from common.categories import CATEGORY_BY_KEY
from database.orm_query import orm_add_expense
from kbds.inline import CancelCallback, CategoryCallback, categories_kb
from kbds.reply import main_menu_kb
from utils.formatter import format_added, format_amount
from utils.parser import parse_expense

user_private_router = Router()

START_TEXT = (
    "👋 Привет! Я помогу вести учёт личных расходов.\n\n"
    "<b>Как записать трату:</b>\n"
    "• <code>1500 Такси</code> — запишу сразу, категорию определю сам\n"
    "• <code>2500</code> — только сумма, категорию выберете кнопками\n\n"
    "<b>Команды:</b>\n"
    "/stats — траты за текущий месяц\n"
    "/undo — удалить последнюю запись"
)

UNKNOWN_TEXT = (
    "Не понял 🤔 Отправьте сумму и, если хотите, описание. "
    "Например: <code>1500 Такси</code> или просто <code>2500</code>."
)


@user_private_router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    # Пользователь уже зарегистрирован в middleware (middlewares/db.py)
    await message.answer(START_TEXT, reply_markup=main_menu_kb())


@user_private_router.message(F.text)
async def add_expense_from_text(message: Message, session: AsyncSession) -> None:
    """Любой текст, который не поймали кнопки меню и команды, пробуем разобрать как расход."""
    parsed = parse_expense(message.text)
    if parsed is None:
        await message.answer(UNKNOWN_TEXT)
        return

    # Вариант Б: пришла только сумма -> спрашиваем категорию кнопками
    if parsed.category is None:
        await message.answer(
            f"Сумма: <b>{format_amount(parsed.amount)}</b>\nВыберите категорию:",
            reply_markup=categories_kb(parsed.amount),
        )
        return

    # Вариант А: сумма + текст -> сохраняем сразу
    expense = await orm_add_expense(
        session,
        user_id=message.from_user.id,
        amount=parsed.amount,
        category=parsed.category.name,
        comment=parsed.comment,
    )
    await message.answer(format_added(expense))


@user_private_router.callback_query(CategoryCallback.filter())
async def choose_category(
    callback: CallbackQuery,
    callback_data: CategoryCallback,
    session: AsyncSession,
) -> None:
    category = CATEGORY_BY_KEY.get(callback_data.key)
    if category is None:
        await callback.answer("Неизвестная категория", show_alert=True)
        return

    expense = await orm_add_expense(
        session,
        user_id=callback.from_user.id,
        amount=callback_data.amount,
        category=category.name,
    )

    # Заменяем сообщение с кнопками на подтверждение, так двойное нажатие невозможно
    if isinstance(callback.message, Message):
        await callback.message.edit_text(format_added(expense))
    await callback.answer("Сохранено")


@user_private_router.callback_query(CancelCallback.filter())
async def cancel_choice(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_text("❌ Отменено, расход не записан.")
    await callback.answer()