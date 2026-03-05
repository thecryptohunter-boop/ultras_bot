import asyncio
import json
import os
import random
from datetime import datetime
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from modules.category_manager import (
    load_categories,
    save_categories,
    get_next_item
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties



class AddToast(StatesGroup):
    waiting_image = State()
    waiting_text = State()


# ===== НАСТРОЙКИ =====

TOKEN = os.getenv("TOKEN")
'''if not TOKEN:
    TOKEN = "ТВОЙ_ЛОКАЛЬНЫЙ_ТОКЕН_ДЛЯ_ТЕСТОВ"'''

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # <-- ID твоего канала

ADMINS = {334306921}

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

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

# ===== ФУНКЦИЯ ПЯТНИЦЫ =====

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


# ===== АВТОПОСТИНГ В КАНАЛ ТОСТ =====

async def post_category(code):
    data = load_categories()
    category = data.get(code)

    if not category:
        return

    item, status = get_next_item(code)

    if status == "empty":
        return

    if status == "finished":
        await bot.send_message(
            list(ADMINS)[0],
            f"⚠️ Закончились материалы в рубрике {category['title']}"
        )
        return

    if status == "stop":
        return

    caption = (
        f"<b>{category['title']}</b>\n\n"
        f"{item['text']}\n\n"
        f"{category['tag']}"
    )

    await bot.send_photo(
        CHANNEL_ID,
        photo=item["file_id"],
        caption=caption
    )


# ===== АВТОПОСТИНГ В КАНАЛ TODAY =====

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


        
# ===== SCHEDULER =====
async def category_scheduler():
    print("CATEGORY SCHEDULER STARTED")

    last_run = {}

    while True:
        now = datetime.now()
        data = load_categories()

        for code, category in data.items():
            s = category["schedule"]

            if (
                now.weekday() in s["weekdays"]
                and now.hour == s["hour"]
                and now.minute == s["minute"]
            ):
                if last_run.get(code) != now.date():
                    last_run[code] = now.date()
                    await post_category(code)

        await asyncio.sleep(30)

async def scheduler():
    print("SCHEDULER STARTED")

    last_today_minute = None
    last_category_minute = None

    while True:
        now = datetime.now()
  #     print("DEBUG TIME:", now.strftime("%H:%M:%S"))
        
        # тест Today — каждые 2 минуты
        if now.minute % 60 == 0 and last_today_minute != now.minute:
            last_today_minute = now.minute
            print("DEBUG: post_today")
            await post_today()

        # тест рубрики — каждые 3 минуты
    '''if now.minute % 1 == 0 and last_category_minute != now.minute:
            last_category_minute = now.minute
            print("DEBUG: post_friday_toast")
            await post_friday_toast()

        await asyncio.sleep(15)'''
        

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

@dp.message(Command("rubrics"))
async def rubrics_help(message: Message):
    if message.from_user.id not in ADMINS:
        return

    text = """
Команды рубрик:

/add friday_toast
/add portrait_fan
/add father_son
/add retro_fans
/add back_in_ussr
/add old_album
/add graffiti_day

/run <код> — запустить вручную
/reset <код> — сбросить индекс
"""
    await message.answer(text)
    
user_states = {}

@dp.message(Command("add"))
async def add_post(message: Message):
    if message.from_user.id not in ADMINS:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажи код рубрики")
        return

    code = args[1]
    user_states[message.from_user.id] = {
        "code": code,
        "step": "photo"
    }

    await message.answer("Отправь фото")

# ===== ПРИЕМ КАРТИНКИ - ПОЛУЧАЕМ ID =====

@dp.message(F.photo)
async def receive_photo(message: Message):
    state = user_states.get(message.from_user.id)
    if not state or state["step"] != "photo":
        return

    file_id = message.photo[-1].file_id
    state["file_id"] = file_id
    state["step"] = "text"

    await message.answer("Теперь отправь текст")

@dp.message()
async def receive_text(message: Message):
    state = user_states.get(message.from_user.id)
    if not state or state["step"] != "text":
        return

    code = state["code"]
    data = load_categories()

    data[code]["items"].append({
        "file_id": state["file_id"],
        "text": message.text
    })

    save_categories(data)
    user_states.pop(message.from_user.id)

    await message.answer("✅ Добавлено")
    await message.reply(f"FILE_ID:\n{file_id}")
    

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






































































































