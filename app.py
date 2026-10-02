import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

# .env нужно загрузить до импорта модулей, которые читают переменные окружения
load_dotenv(find_dotenv())

from common.bot_cmd_list import private
from database.engine import create_db, session_maker
from handlers.menu_processing import menu_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Боту нужны только сообщения и нажатия на inline-кнопки
ALLOWED_UPDATES = ["message", "callback_query"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Укажите его в файле .env")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

# Порядок важен: menu_router (кнопки меню, /stats, /undo) подключаем раньше,
# чем user_private_router, где лежит обработчик свободного текста "1500 Такси".
# Иначе нажатие на "📊 Статистика" уйдёт в парсер суммы.
dp.include_router(menu_router)
dp.include_router(user_private_router)


async def on_startup() -> None:
    # Создаёт таблицы users и expenses, если их ещё нет (данные не удаляются)
    await create_db()
    logger.info("База данных готова")


async def on_shutdown() -> None:
    logger.info("Бот остановлен")


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Middleware передаёт сессию БД в каждый хендлер
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # Убираем накопившиеся апдейты, пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)

    # Меню команд в Telegram (/start, /stats, /undo)
    await bot.set_my_commands(
        commands=private,
        scope=types.BotCommandScopeAllPrivateChats(),
    )

    logger.info("Бот запущен")
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную")