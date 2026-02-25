import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime
import json
import random

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"  # токен от BotFather

bot = Bot(token=TOKEN)
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())