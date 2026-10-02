from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # Время во всех таблицах хранится в UTC (CURRENT_TIMESTAMP в SQLite отдаёт UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class User(Base):
    """Пользователи бота. user_id совпадает с Telegram ID."""

    __tablename__ = "users"

    # Telegram ID задаём вручную, поэтому autoincrement отключён
    user_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Expense(Base):
    """Расходы пользователей."""

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(nullable=False)  # REAL в SQLite
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="expenses")

    # Ускоряет статистику за месяц и поиск последней записи для /undo
    __table_args__ = (Index("ix_expenses_user_created", "user_id", "created_at"),)