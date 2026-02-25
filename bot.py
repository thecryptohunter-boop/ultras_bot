import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.filters import Command
from datetime import datetime
import json
import random
import os

TOKEN = ""
CHANNEL_ID = -1003585308639  # <-- ВСТАВЬ СЮДА ID КАНАЛА

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Загружаем базы
with open("history.json", encoding="utf-8") as f:
    history_db = json.load(f)

with open("ultras.json", encoding="utf-8") as f:
    ultras_db = json.load(f)

# --- Главное меню ---
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🏟 Ультрас-группировки")],
        [types.KeyboardButton(text="⚽ Сегодня в истории")],
        [types.KeyboardButton(text="🕶 Прислать историю")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Добро пожаловать в фанатский архив ⚽", reply_markup=keyboard)

# --- Ультрас-группировки ---
@dp.message(lambda m: m.text == "🏟 Ультрас-группировки")
async def ultras(message: types.Message):
    regions = list(ultras_db.keys())
    text = "Выбери регион:\n" + "\n".join([f"• {r}" for r in regions])
    await message.answer(text)

# --- Выбор региона ---
@dp.message(lambda m: m.text in ultras_db)
async def region_choice(message: types.Message):
    region = message.text
    groups = ultras_db[region]
    text = "\n".join([f"{g['name']} — {g['info']}" for g in groups])
    await message.answer(text)

# --- Сегодня в истории ---
@dp.message(lambda m: m.text == "⚽ Сегодня в истории")
async def today_history(message: types.Message):
    today = datetime.now().strftime("%m-%d")
    events = history_db.get(today, ["Сегодня без крупных фанатских событий."])
    # Можно выводить случайное событие, чтобы каждый день было динамично
    await message.answer(random.choice(events))

# --- Анонимная история ---
@dp.message(lambda m: m.text == "🕶 Прислать историю")
async def send_story(message: types.Message):
    await message.answer("Отправь свою историю прямо сюда, а мы опубликуем её анонимно в канале!")

async def today_post():
    today = datetime.now().strftime("%d.%m")

    text = f"""
📅 <b>Сегодня в истории ультрас</b>

<b>{today}</b>

В этот день фанаты устроили культовые перфомансы, вошедшие в историю трибун.

⚽ Страсть. Верность. Движ.
"""

    await bot.send_message(chat_id=CHANNEL_ID, text=text)


async def scheduler():
    while True:
        now = datetime.now()

        # пост каждый день в 12:00
        if now.hour == 12 and now.minute == 0:
            await today_post()
            await asyncio.sleep(60)

        await asyncio.sleep(20)


async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())











