import asyncio
import json
import os
import random
from datetime import datetime
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode


# ===== НАСТРОЙКИ =====

TOKEN = os.getenv("TOKEN")
'''if not TOKEN:
    TOKEN = "ТВОЙ_ЛОКАЛЬНЫЙ_ТОКЕН_ДЛЯ_ТЕСТОВ"'''

CHANNEL_ID = -1003585308639  # <-- ID твоего канала

# ===== ЗАГРУЖАЕМ КАРТИНКИ =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_today_image():
    weekday = datetime.now().weekday() + 1
    path = os.path.join(BASE_DIR, "images", f"{weekday:02d}.jpg")
    print("DEBUG IMAGE PATH:", path)
    print("FILE EXISTS:", os.path.exists(path))
    return path
    
# ===== ЗАГРУЖАЕМ JSON СОБЫТИЯ =====

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
        [KeyboardButton(text="📅 Сегодня в истории")], 
     '''[KeyboardButton(text="🏟 Ультрас-группировки")],       
        [KeyboardButton(text="👑 Легенды движения")],
        [KeyboardButton(text="⚔ Дерби")],
        [KeyboardButton(text="📰 Новости")],'''
    ],
    resize_keyboard=True
)

# ===== ФУНКЦИЯ ГЕНЕРАЦИИ ПОСТА =====

def generate_today_post():
    today = datetime.now().strftime("%d.%m")
    events = EVENTS.get(today)

    if not events:
        return f"""
📅 <b>СЕГОДНЯШНЯЯ ДАТА {today} 🔈 в истории ультрас:</b>


🔥 Событий на сегодня в базе <b>ET VIVIT</b> не найдено.


⚽ <i>Страсть. Верность. Движ. 
✍🏻 Подпишись если не Кузьмич: @EtVivit</i>


#UltrasToday
"""
 

# Берём 6 событий
    selected_events = events[:6]

    text = f"""
📅 <b>СЕГОДНЯШНЯЯ ДАТА {today} 🔈 в истории ультрас:</b>


"""  
    for i, event in enumerate(selected_events, 1):
        text += (
            f"{i}️⃣ <b>{event['year']}, {event['club']}</b>\n\n"
            f"⚽ {event['text']}\n\n\n"
        )

    text += (
        "🔥 <i>Страсть. Верность. Движ.\n"
        "✍🏻 Подпишись если не Кузьмич: @EtVivit</i>\n\n\n"
        "#UltrasToday"
    )

    return text

# ===== АВТОПОСТИНГ В КАНАЛ =====

async def post_today():
    text = generate_today_post()
    image_path = get_today_image()

    await bot.send_photo(
        CHANNEL_ID,
        photo=FSInputFile(image_path),
        caption="📅 Сегодня в истории ультрас",
        parse_mode="HTML"
    )
    await asyncio.sleep(1)
    await bot.send_message(
        CHANNEL_ID,
        text,
        parse_mode="HTML"
    )


async def scheduler():
    while True:
        now = datetime.now()

        # публикация каждый день в 12:00
        if now.minute % 6 == 0:
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














































