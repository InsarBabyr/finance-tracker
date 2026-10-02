from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm_query import orm_add_user


class DataBaseSession(BaseMiddleware):
    """Открывает сессию БД на каждый апдейт и передаёт её в хендлер как `session`.

    Заодно регистрирует пользователя: при первом сообщении он попадает в таблицу
    users, при смене ника в Telegram username обновляется.
    """

    def __init__(self, session_pool: async_sessionmaker) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session

            # event_from_user заполняет встроенный middleware aiogram
            tg_user: TgUser | None = data.get("event_from_user")
            if tg_user is not None and not tg_user.is_bot:
                await orm_add_user(
                    session,
                    user_id=tg_user.id,
                    username=tg_user.username,
                )

            return await handler(event, data)