import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from modules.scheduler import scheduler
from modules.admin_commands import register_admin_handlers
from modules.config import TOKEN, CHANNEL_ID, ADMINS

# ===== ИНИЦИАЛИЗАЦИЯ =====

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

register_admin_handlers(dp, bot, ADMINS)

# ===== ЗАГРУЖАЕМ КАРТИНКИ =====

def get_today_image():

    weekday = datetime.now().weekday() + 1
    path = f"images/{weekday:02d}.jpg"

    return path
    
# ===== ЗАГРУЖАЕМ JSON СОБЫТИЯ =====

def load_events():
    with open("events.json", "r", encoding="utf-8") as f:
        return json.load(f)

EVENTS = load_events()



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
📅 <b>СЕГОДНЯШНИЙ ДЕНЬ {today} 🔈 в истории ультрас:</b>


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


# ===== Для Админов =====

async def notify_admins(text):
    for admin_id in ADMINS:
        await bot.send_message(admin_id, text)


# ===== АВТОПОСТИНГ В КАНАЛ TODAY =====

async def post_today():

    text = generate_today_post()
    image = get_today_image()

    await bot.send_photo(
        CHANNEL_ID,
        photo=FSInputFile(image),
        caption="",
        parse_mode="HTML"
    )

    await bot.send_message(
        CHANNEL_ID,
        text,
        parse_mode="HTML"
    )
        
# ===== УЛЬТРАС АССИСТЕНТ ===========

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Сегодня в истории")], 
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
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
    
# ===== АВТОПОСТИНГ РУБРИКИ =====



async def main():

    asyncio.create_task(
        scheduler(post_today, bot, CHANNEL_ID, ADMINS)
    )

    await dp.start_polling(bot)

# ===== ЗАПУСК =====

if __name__ == "__main__":
    asyncio.run(main())















































































































