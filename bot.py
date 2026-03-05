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

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # <-- ID твоего канала

ADMINS = {334306921}

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# ===== ИНИЦИАЛИЗАЦИЯ =====

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


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


# ===== АВТОПОСТИНГ РУБРИКИ =====

async def post_category(name):

    data = load_categories()
    cat = data[name]

    posts = cat["posts"]

    if not posts:
        return

    index = cat["last_index"] + 1

    if index >= len(posts):
        index = 0

    post = posts[index]

    await bot.send_photo(
        CHANNEL_ID,
        photo=post["file_id"],
        caption=post["text"],
        parse_mode="HTML"
    )

    cat["last_index"] = index

    save_categories(data)


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

    while True:

        now = datetime.now()
        weekday = now.weekday()

        data = load_categories()

        for name, cat in data.items():

            if (
                cat["day"] == weekday
                and cat["hour"] == now.hour
                and cat["minute"] == now.minute
            ):
                await post_category(name)

        await asyncio.sleep(60)

async def scheduler():
    print("SCHEDULER STARTED")

    last_today_minute = None

    while True:
        now = datetime.now()
  #     print("DEBUG TIME:", now.strftime("%H:%M:%S"))
        
        # тест Today — каждые 2 минуты
        if now.minute % 10 == 0 and last_today_minute != now.minute:
            last_today_minute = now.minute
            print("DEBUG: post_today")
            await post_today()
        

# ===== ХЕНДЛЕРЫ =====

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🤖 Ультрас-ассистент активен.\n\nВыбери раздел:",
        reply_markup=main_kb
    )


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

# ===== КОМАНДА ДОБАВЛЕНИЯ РУБРИК =====

user_states = {}

@dp.message(Command("add"))
async def add_menu(message: Message):

    rubrics = [
        "portrait_fan",
        "retro_fans",
        "ussr_back",
        "old_album",
        "father_son",
        "graffiti_day",
        "friday_toast"
    ]

    text = "Выберите рубрику:\n\n"

    for r in rubrics:
        text += f"/add_{r}\n"

    await message.answer(text)

@dp.message(F.text.startswith("/add_"))
async def add_rubric(message: Message):

    rubric = message.text.replace("/add_", "")

    upload_state[message.from_user.id] = {
        "rubric": rubric,
        "step": "photo"
    }

    await message.answer("Отправьте фото")


# ===== ПРИЕМ КАРТИНКИ =====

@dp.message(F.photo)
async def receive_photo(message: Message):

    user = message.from_user.id

    if user not in upload_state:
        return

    state = upload_state[user]

    if state["step"] != "photo":
        return

    file_id = message.photo[-1].file_id

    state["file_id"] = file_id
    state["step"] = "text"

    await message.answer("Теперь отправьте текст")

# ===== ПРИЕМ ТЕКСТА =====

@dp.message(F.text)
async def receive_text(message: Message):

    user = message.from_user.id

    if user not in upload_state:
        return

    state = upload_state[user]

    if state["step"] != "text":
        return

    rubric = state["rubric"]

    data = load_categories()

    data[rubric]["posts"].append({
        "file_id": state["file_id"],
        "text": message.text
    })

    save_categories(data)

    await message.answer("Пост добавлен!")

    del upload_state[user]
    await message.reply(f"FILE_ID:\n{state['file_id']}")
    

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
    asyncio.create_task(category_scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())









































































































