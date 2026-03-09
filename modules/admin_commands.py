from aiogram.filters import Command
from aiogram.types import Message
from modules.category_manager import add_post
from modules.storage import load_categories, save_categories

user_states = {}


def register_admin_handlers(dp, bot, ADMINS):

    # ===== АДМИН МЕНЮ =====

    @dp.message(Command("admin"))
    async def admin_panel(message: Message):

        if message.from_user.id not in ADMINS:
            return

        text = 
⚙️ <b>АДМИН ПАНЕЛЬ</b>

Добавление постов:

/add friday_toast
/add portrait_fan
/add father_son
/add retro_fans
/add back_in_ussr
/add old_album
/add graffiti_day
/add legends
/add stadiums

Управление:

/run <код> — пост сейчас
/setindex <код> <номер>
/reload — перечитать JSON
/stats — статистика


        await message.answer(text)

    # ===== ДОБАВЛЕНИЕ ПОСТА =====

    @dp.message(Command("add"))
    async def add_start(message: Message):

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

        await message.answer("📷 Отправь фото")

    # ===== ПОЛУЧЕНИЕ ФОТО =====

    @dp.message(lambda m: m.photo)
    async def receive_photo(message: Message):

        state = user_states.get(message.from_user.id)

        if not state or state["step"] != "photo":
            return

        file_id = message.photo[-1].file_id

        state["file_id"] = file_id
        state["step"] = "text"

        await message.answer("✏️ Теперь отправь текст")
        await message.reply(f"FILE_ID:\n{file_id}")

    # ===== ПОЛУЧЕНИЕ ТЕКСТА =====

    @dp.message()
    async def receive_text(message: Message):

        state = user_states.get(message.from_user.id)

        if not state or state["step"] != "text":
            return

        code = state["code"]
        file_id = state["file_id"]
        text = message.text

        add_post(code, file_id, text)

        user_states.pop(message.from_user.id)

        await message.answer("✅ Пост добавлен")

    # ===== СБРОС ИНДЕКСА =====

    @dp.message(Command("setindex"))
    async def set_index(message: Message):

        if message.from_user.id not in ADMINS:
            return

        args = message.text.split()

        if len(args) != 3:
            await message.answer("Пример:\n/setindex friday_toast 3")
            return

        code = args[1]
        index = int(args[2])

        data = load_categories()

        data[code]["last_index"] = index

        save_categories(data)

        await message.answer("✅ Индекс обновлён")

    # ===== РЕЛОАД JSON =====

    @dp.message(Command("reload"))
    async def reload_json(message: Message):

        if message.from_user.id not in ADMINS:
            return

        load_categories()

        await message.answer("♻️ JSON перезагружен")

    # ===== СТАТИСТИКА =====

    @dp.message(Command("stats"))
    async def stats(message: Message):

        if message.from_user.id not in ADMINS:
            return

        data = load_categories()

        text = "📊 СТАТИСТИКА\n\n"

        for code, cat in data.items():

            total = len(cat["posts"])
            index = cat["last_index"]

            text += f"{cat['title']}\n"
            text += f"Постов: {total}\n"
            text += f"Опубликовано: {index + 1}\n\n"

        await message.answer(text)
       
