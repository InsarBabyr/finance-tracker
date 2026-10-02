from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    key: str            # короткий ключ для callback_data (до 64 байт в Telegram)
    emoji: str
    name: str           # это значение сохраняется в expenses.category
    description: str
    keywords: tuple[str, ...] = ()  # слова для автоопределения категории по тексту

    @property
    def title(self) -> str:
        """Название с эмодзи для показа пользователю."""
        return f"{self.emoji} {self.name}"


# Порядок совпадает с ТЗ и определяет порядок кнопок
CATEGORIES: tuple[Category, ...] = (
    Category(
        "market", "🛒", "Супермаркеты",
        "продукты, мелкие бытовые покупки",
        ("продукты", "супермаркет", "магнум", "small", "смолл", "мясо",
         "овощи", "фрукты", "хлеб", "молоко"),
    ),
    Category(
        "cafe", "🍽", "Кафе и Рестораны",
        "общепит, доставки еды, кофе",
        ("кафе", "ресторан", "кофе", "обед", "ужин", "завтрак", "пицца",
         "бургер", "суши", "wolt", "glovo", "глово", "доставка"),
    ),
    Category(
        "transport", "🚌", "Транспорт",
        "такси, автобус, LRT",
        ("такси", "indrive", "индрайвер", "автобус", "lrt", "метро",
         "бензин", "парковка", "проезд"),
    ),
    Category(
        "kaspi", "🔴", "Kaspi Магазин",
        "заказы и покупки через Kaspi",
        ("kaspi", "каспи"),
    ),
    Category(
        "shopping", "🛍", "Покупки и Одежда",
        "вещи, гардероб, личные покупки",
        ("одежда", "обувь", "куртка", "футболка", "джинсы", "кроссовки"),
    ),
    Category(
        "fun", "🎬", "Развлечения",
        "кино, игры, досуг, хобби",
        ("кино", "игра", "игры", "боулинг", "концерт", "steam"),
    ),
    Category(
        "pharmacy", "💊", "Аптека",
        "лекарства, здоровье",
        ("аптека", "лекарства", "таблетки", "витамины", "врач"),
    ),
    Category(
        "subs", "📱", "Подписки",
        "ИИ сервисы, музыка, iCloud и т.д.",
        ("подписка", "chatgpt", "claude", "spotify", "netflix", "icloud",
         "youtube", "apple"),
    ),
    Category(
        "other", "📦", "Другое",
        "прочие незапланированные траты",
    ),
)

DEFAULT_CATEGORY = CATEGORIES[-1]  # "Другое"

CATEGORY_BY_KEY = {c.key: c for c in CATEGORIES}
CATEGORY_BY_NAME = {c.name.lower(): c for c in CATEGORIES}


def match_category(text: str) -> Category | None:
    """Пытается определить категорию по тексту ("Такси" -> Транспорт).

    Сначала ищет точное совпадение с названием категории, затем по ключевым словам.
    Если ничего не найдено, возвращает None.
    """
    text = text.strip().lower()
    if not text:
        return None
    if text in CATEGORY_BY_NAME:
        return CATEGORY_BY_NAME[text]
    for category in CATEGORIES:
        if any(word in text for word in category.keywords):
            return category
    return None


def title_by_name(name: str) -> str:
    """Название категории из БД -> название с эмодзи (для статистики)."""
    category = CATEGORY_BY_NAME.get(name.lower())
    return category.title if category else name