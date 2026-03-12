from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from modules.category_manager import add_post, post_category
from modules.storage import load_categories, save_categories

user_states = {}

print("ADMIN MODULE LOADED")
def register_admin_handlers(dp, bot, ADMINS, CHANNEL_ID):

    # ===== ГЛАВНАЯ АДМИН ПАНЕЛЬ =====

    def admin_keyboard():

        keyboard = [
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="menu:add"),
                InlineKeyboardButton(text="👁 Preview", callback_data="menu:preview")
            ],
            [
                InlineKeyboardButton(text="🚀 Опубликовать", callback_data="menu:run"),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data="menu:edit")
            ],
            [
                InlineKeyboardButton(text="🔢 Индекс", callback_data="menu:setindex"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="menu:stats")
            ],
            [
                InlineKeyboardButton(text="🗑 Удалить", callback_data="menu:delete"),
                InlineKeyboardButton(text="♻️ Reload", callback_data="menu:reload")
            ],
            [
                InlineKeyboardButton(text="🔥 RUN ALL", callback_data="menu:runall")
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    # ===== МЕНЮ РУБРИК =====

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

    # ===== ADMIN COMMAND =====

    @dp.message(Command("admin"))
    async def admin_panel(message: Message):

        if message.from_user.id not in ADMINS:
            return

        await message.answer(
            "⚙️ АДМИН ПАНЕЛЬ",
            reply_markup=admin_keyboard()
        )

    # ===== ПОЛУЧЕНИЕ ФОТО =====

    @dp.message(lambda m: m.photo)
    async def receive_photo(message: Message):

        state = user_states.get(message.from_user.id)

        if not state or state.get("step") != "photo":
            return

        file_id = message.photo[-1].file_id

        state["file_id"] = file_id
        state["step"] = "text"

        await message.answer("✏️ Теперь отправь текст")

    # ===== ПОЛУЧЕНИЕ ТЕКСТА =====

    @dp.message(lambda m: m.from_user.id in user_states and m.text)
    async def receive_text(message: Message):

        state = user_states.get(message.from_user.id)

        if not state:
            return

        # ===== EDIT =====

        if state.get("action") == "edit":

            data = load_categories()

            code = state["code"]
            index = state["index"]

            data[code]["posts"][index]["text"] = message.text

            save_categories(data)

            user_states.pop(message.from_user.id)

            await message.answer("✅ Пост обновлён")

            return

        # ===== SETINDEX =====

        if state.get("action") == "setindex":

            code = state["code"]

            try:
                index = int(message.text)
            except:
                await message.answer("❌ Нужно число")
                return

            data = load_categories()

            data[code]["last_index"] = index

            save_categories(data)

            user_states.pop(message.from_user.id)

            await message.answer("✅ Индекс обновлён")

            return

        # ===== ADD POST =====

        if state.get("step") == "text":

            code = state["code"]
            file_id = state["file_id"]

            add_post(code, file_id, message.text)

            user_states.pop(message.from_user.id)

            await message.answer("✅ Пост добавлен")

        # ===== CALLBACK HANDLER =====

    @dp.callback_query(lambda c: not c.data.startswith("json_"))
    async def callback_router(callback: CallbackQuery):
    
        if callback.from_user.id not in ADMINS:
            return
    
        data = callback.data

        # пропускаем JSON callbacks
        if data.startswith("json_"):
            return
    
        # ===== DELETE CONFIRM =====
    
        if data == "confirm_delete":
    
            state = user_states.get(callback.from_user.id)
    
            if not state or state.get("action") != "delete":
                await callback.answer()
                return
    
            code = state["code"]
            index = state["index"]
    
            categories = load_categories()
    
            categories[code]["posts"].pop(index)
    
            save_categories(categories)
    
            user_states.pop(callback.from_user.id)
    
            await callback.message.answer("🗑 Пост удалён")
    
            await callback.answer()
    
            return

        # ===== ГЛАВНОЕ МЕНЮ =====

        if data.startswith("menu:"):

            action = data.split(":")[1]

            if action == "reload":

                load_categories()

                await callback.message.answer("♻️ JSON перечитан")

            elif action == "runall":

                categories = load_categories()

                for code in categories:
                    await post_category(bot, CHANNEL_ID, ADMINS, code)

                await callback.message.answer("✅ Все рубрики опубликованы")

            elif action == "stats":

                categories = load_categories()

                text = "📊 СТАТИСТИКА\n\n"

                for code, cat in categories.items():

                    total = len(cat["posts"])
                    index = cat.get("last_index", -1)

                    text += f"{cat['title']}\n"
                    text += f"Постов: {total}\n"
                    text += f"Опубликовано: {index + 1}\n\n"

                await callback.message.answer(text)

            else:

                await callback.message.answer(
                    "Выбери рубрику:",
                    reply_markup=categories_menu(action)
                )

            await callback.answer()
            return

        # ===== РУБРИКИ =====

        if ":" not in data:
            await callback.answer()
            return

        action, code = data.split(":")

        categories = load_categories()

        if code not in categories:
            await callback.answer()
            return

        cat = categories[code]

        # ===== RUN =====

        if action == "run":

            await post_category(bot, CHANNEL_ID, ADMINS, code)

            await callback.message.answer(f"✅ {code} опубликован")

        # ===== PREVIEW =====

        elif action == "preview":

            index = cat.get("last_index", -1) + 1

            if index >= len(cat["posts"]):

                await callback.message.answer("⚠️ Постов больше нет")

            else:

                post = cat["posts"][index]

                caption = f"{cat['title']}\n\n{post['text']}\n\n\n{cat['tag']}"

                await bot.send_photo(
                    callback.message.chat.id,
                    photo=post["file_id"],
                    caption=caption
                )

        # ===== ADD =====

        elif action == "add":

            user_states[callback.from_user.id] = {
                "code": code,
                "step": "photo"
            }

            await callback.message.answer("📷 Отправь фото")

        # ===== EDIT =====

        elif action == "edit":

            index = cat.get("last_index", -1) + 1

            if index >= len(cat["posts"]):

                await callback.message.answer("⚠️ Постов больше нет")

            else:

                post = cat["posts"][index]

                user_states[callback.from_user.id] = {
                    "action": "edit",
                    "code": code,
                    "index": index
                }

                await bot.send_photo(
                    callback.message.chat.id,
                    photo=post["file_id"],
                    caption=f"Редактируем:\n\n{post['text']}"
                )

                await callback.message.answer("✏️ Отправь новый текст")

        # ===== SETINDEX =====

        elif action == "setindex":

            user_states[callback.from_user.id] = {
                "action": "setindex",
                "code": code
            }

            await callback.message.answer("🔢 Введи новый индекс")

        # ===== DELETE =====

        elif action == "delete":

            index = cat.get("last_index", -1) + 1

            if index >= len(cat["posts"]):

                await callback.message.answer("⚠️ Постов больше нет")

            else:

                post = cat["posts"][index]

                user_states[callback.from_user.id] = {
                    "action": "delete",
                    "code": code,
                    "index": index
                }

                await bot.send_photo(
                    callback.message.chat.id,
                    photo=post["file_id"],
                    caption=f"Удалить этот пост?\n\n{post['text']}"
                )

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="❌ Удалить",
                                callback_data="confirm_delete"
                            )
                        ]
                    ]
                )

                await callback.message.answer(
                    "Подтвердить удаление?",
                    reply_markup=keyboard
                )


        await callback.answer()
