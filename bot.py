import asyncio
import json
import os
import random
from datetime import datetime
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

from modules.category_manager import get_post_for_today


# ===== НАСТРОЙКИ =====

TOKEN = os.getenv("TOKEN")
'''if not TOKEN:
    TOKEN = "ТВОЙ_ЛОКАЛЬНЫЙ_ТОКЕН_ДЛЯ_ТЕСТОВ"'''

CHANNEL_ID = "CHANNEL_ID"  # <-- ID твоего канала

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
    ],
    resize_keyboard=True
)

# ===== ФУНКЦИЯ ГЕНЕРАЦИИ ПОСТА =====

def generate_today_post():
    today = datetime.now().strftime("%d.%m")
    events = EVENTS.get(today)

    if not events:
        return f"""
📅 <b>СЕГОДНЯШНИЙ ДЕНЬ {today} 🔈 в истории ультрас:</b>


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
        caption="",
        parse_mode="HTML"
    )

    await bot.send_message(
        CHANNEL_ID,
        text,
        parse_mode="HTML"
    )


async def post_daily_category():
    post = get_post_for_today()
    if not post:
        return

    if post.get("file_id"):
        await bot.send_photo(
            CHANNEL_ID,
            photo=post["file_id"],
            caption=post["text"],
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            CHANNEL_ID,
            post["text"],
            parse_mode="HTML"
        )
        
# ===== SCHEDULER =====

async def scheduler():
    print("SCHEDULER STARTED")

    last_today_minute = None
    last_category_minute = None

    while True:
        now = datetime.now()

        # тест Today — каждые 2 минуты
        if now.minute % 2 == 0 and last_today_minute != now.minute:
            last_today_minute = now.minute
            print("DEBUG: post_today")
            await post_today()

        # тест рубрики — каждые 5 минут
        if now.minute % 5 == 0 and last_category_minute != now.minute:
            last_category_minute = now.minute
            print("DEBUG: post_daily_category")
            await post_daily_category()

        await asyncio.sleep(15)
        
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


'''@dp.message(F.text == "🏟 Ультрас-группировки")
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
    await message.answer("Раздел в разработке 🔧\nФан-новости и движ.")'''

# ===== ПРОВЕРКА ID ФОТО =====

'''@dp.message_handler(content_types=['photo'], state=SetCategoryImage.waiting_photo)
async def set_category_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = data['code']

    file_id = message.photo[-1].file_id

    set_category_image(code, file_id)

    await message.answer("Картинка сохранена.")
    await state.finish()'''
    
# ===== ЗАПУСК =====

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())








































































