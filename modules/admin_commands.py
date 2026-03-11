from aiogram.filters import Command
from aiogram.types import Message
from modules.category_manager import add_post
from modules.storage import load_categories, save_categories
from modules.category_manager import post_category
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

user_states = {}


def register_admin_handlers(dp, bot, ADMINS, CHANNEL_ID):

    # ===== АДМИН МЕНЮ =====

    @dp.message(Command("admin"))
    async def admin_panel(message: Message):

        if message.from_user.id not in ADMINS:
            return

        data = load_categories()

        text = """
    ⚙️ <b>АДМИН ПАНЕЛЬ</b>

    Добавление постов:
    """

        for code in data:
            text += f"/add {code}\n"

        text += """

    Управление:

    /preview friday_toast - предпросмотр
    /run friday_toast — пост сейчас
    /runall — запустить все сразу
    /setindex friday_toast 3
    /reload — перечитать JSON
    /stats — статистика
    """

        await message.answer(text)

  # ===== INLINE BUTTONS =====
    
    def categories_menu(action):

    data = load_categories()

    buttons = []

    for code in data:
        buttons.append(
            [InlineKeyboardButton(
                text=code,
                callback_data=f"{action}:{code}"
            )]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

    
    # ===== ДОБАВЛЕНИЕ ПОСТА =====

    @dp.message(Command("add"))
    async def add_menu(message: Message):

    if message.from_user.id not in ADMINS:
        return

    await message.answer(
        "Выбери рубрику:",
        reply_markup=categories_menu("add")
    )

    # ===== ПОЛУЧЕНИЕ ФОТО =====

    @dp.message(lambda m: m.photo and not m.text)
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

    @dp.message(lambda m: m.from_user.id in user_states and m.text)
    async def receive_text(message: Message):

        state = user_states.get(message.from_user.id)

        if not state or state["step"] != "text":
            return

        # EDIT MODE
        if state.get("action") == "edit":
        
            data = load_categories()
        
            code = state["code"]
            index = state["index"]
        
            data[code]["posts"][index]["text"] = message.text
        
            save_categories(data)
        
            user_states.pop(message.from_user.id)
        
            await message.answer("✅ Пост обновлён")
        
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

        await message.answer("♻️ JSON перечитан")
   
    # ===== EDIT =====

    @dp.message(Command("edit"))
    async def edit_menu(message: Message):

        if message.from_user.id not in ADMINS:
            return

        await message.answer(
            "Выбери рубрику:",
            reply_markup=categories_menu("edit")
        )
    
    
    
    # ===== PREVIEW =====
    
    @dp.message(Command("preview"))
    async def preview_menu(message: Message):

    if message.from_user.id not in ADMINS:
        return

    await message.answer(
        "Выбери рубрику:",
        reply_markup=categories_menu("preview")
    )
    
    # ===== СТАТИСТИКА =====

    @dp.message(Command("stats"))
    async def stats(message: Message):

        if message.from_user.id not in ADMINS:
            return

        data = load_categories()

        text = "📊 СТАТИСТИКА\n\n"

        for code, cat in data.items():

            total = len(cat["posts"])
            index = cat.get("last_index", -1)

            text += f"{cat['title']}\n"
            text += f"Постов: {total}\n"
            text += f"Опубликовано: {index + 1}\n\n"

        await message.answer(text)
    
    # ===== RUN ===== 
    
    @dp.message(Command("run"))
    async def run_menu(message: Message):

        if message.from_user.id not in ADMINS:
            return

        await message.answer(
            "Выбери рубрику:",
            reply_markup=categories_menu("run")
        )

    # ===== RUN ALL CATS ===== 
    
    @dp.message(Command("runall"))
    async def run_all(message: Message):

        if message.from_user.id not in ADMINS:
            return

        data = load_categories()

        for code in data:
            await post_category(bot, CHANNEL_ID, ADMINS, code)

        await message.answer("✅ Все рубрики опубликованы")

    @dp.callback_query(lambda c: ":" in c.data)
    async def category_action(callback: CallbackQuery):

        action, code = callback.data.split(":")
    
        if action == "run":
    
            await post_category(bot, CHANNEL_ID, ADMINS, code)
    
            await callback.message.answer(f"✅ {code} опубликован")
    
        elif action == "edit":

            data = load_categories()
        
            cat = data[code]
        
            index = cat.get("last_index", -1) + 1
        
            if index >= len(cat["posts"]):
                await callback.message.answer("⚠️ Постов больше нет")
                return
        
            post = cat["posts"][index]
        
            user_states[callback.from_user.id] = {
                "action": "edit",
                "code": code,
                "index": index
            }
        
            await bot.send_photo(
                callback.message.chat.id,
                photo=post["file_id"],
                caption=f"Редактируем пост:\n\n{post['text']}"
            )
    
            await callback.message.answer("✏️ Отправь новый текст")
            
        elif action == "preview":
    
            data = load_categories()
            cat = data[code]
    
            index = cat.get("last_index", -1) + 1
    
            if index >= len(cat["posts"]):
                await callback.message.answer("⚠️ Постов больше нет")
                return
    
            post = cat["posts"][index]
    
            caption = f"{cat['title']}\n\n{post['text']}\n\n{cat['tag']}"
    
            await bot.send_photo(
                callback.message.chat.id,
                photo=post["file_id"],
                caption=caption
            )
    
        elif action == "add":
    
            user_states[callback.from_user.id] = {
                "code": code,
                "step": "photo"
            }
    
            await callback.message.answer("📷 Отправь фото")
    
        await callback.answer()
