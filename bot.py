import asyncio
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode


# ===== НАСТРОЙКИ =====

TOKEN = os.getenv("TOKEN")
'''if not TOKEN:
    TOKEN = "ТВОЙ_ЛОКАЛЬНЫЙ_ТОКЕН_ДЛЯ_ТЕСТОВ"'''

CHANNEL_ID = -1003585308639  # <-- ID твоего канала

# ===== ЗАГРУЖАЕМ JSON =====

def load_events():
    with open("events.json", "r", encoding="utf-8") as f:
        return json.load(f)

EVENTS = load_events()

# ===== ИНИЦИАЛИЗАЦИЯ =====

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# ===== КНОПКИ =====

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏟 Ультрас-группировки")],
        [KeyboardButton(text="📅 Сегодня в истории")],
        [KeyboardButton(text="👑 Легенды движения")],
        [KeyboardButton(text="⚔ Дерби")],
        [KeyboardButton(text="📰 Новости")],
    ],
    resize_keyboard=True
)

# ===== ФУНКЦИЯ ГЕНЕРАЦИИ ПОСТА =====

def generate_today_post():
    today = datetime.now().strftime("%d.%m")
    events = EVENTS.get(today)

    if not events:
        return f"""
📅 <b>Сегодня в истории ультрас</b>

<b>{today}</b>

В этот день происходили события, формировавшие культуру фан-движений Европы и Южной Америки.

⚽ Страсть. Верность. Движ.
"""

    event = random.choice(events)

    return f"""
📅 <b>Сегодня в истории ультрас</b>

<b>{today}</b>

<b>{event['club']}, {event['year']}</b>

{event['text']}

⚽ Страсть. Верность. Движ.

# ===== АВТОПОСТИНГ В КАНАЛ =====

async def post_today():
    text = generate_today_post()
    await bot.send_message(chat_id=CHANNEL_ID, text=text)


async def scheduler():
    while True:
        now = datetime.now()

        # публикация каждый день в 12:00
        if now.hour == 12 and now.minute == 0:
            await post_today()
            await asyncio.sleep(60)

        await asyncio.sleep(20)


# ===== ХЕНДЛЕРЫ =====

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "🤖 Ультрас-ассистент активен.\n\nВыбери раздел:",
        reply_markup=main_kb
    )


@dp.message(F.text == "📅 Сегодня в истории")
async def today_handler(message: Message):
    text = generate_today_post()
    await message.answer(text)


@dp.message(F.text == "🏟 Ультрас-группировки")
async def ultras_handler(message: Message):
    await message.answer("Раздел в разработке 🔧\nСкоро будет большая база группировок.")


@dp.message(F.text == "👑 Легенды движения")
async def legends_handler(message: Message):
    await message.answer("Раздел в разработке 🔧\nБудут культовые фигуры фан-сцены.")


@dp.message(F.text == "⚔ Дерби")
async def derby_handler(message: Message):
    await message.answer("Раздел в разработке 🔧\nИстории главных противостояний.")


@dp.message(F.text == "📰 Новости")
async def news_handler(message: Message):
    await message.answer("Раздел в разработке 🔧\nФан-новости и движ.")


# ===== ЗАПУСК =====

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

