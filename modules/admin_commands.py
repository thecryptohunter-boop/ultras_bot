from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command

from modules.category_manager import add_post


def register_admin_handlers(dp, bot, ADMINS):

    user_states = {}

    def is_admin(user_id):
        return user_id in ADMINS


    @dp.message(Command("add"))
    async def add_handler(message: Message):

        if not is_admin(message.from_user.id):
            return

        args = message.text.split()

        if len(args) < 2:
            await message.answer("Использование:\n/add CODE")
            return

        code = args[1]

        user_states[message.from_user.id] = {
            "step": "photo",
            "code": code
        }

        await message.answer("Отправь фото")


    @dp.message(F.photo)
    async def receive_photo(message: Message):

        state = user_states.get(message.from_user.id)

        if not state:
            return

        if state["step"] != "photo":
            return

        file_id = message.photo[-1].file_id

        state["file_id"] = file_id
        state["step"] = "text"

        await message.answer("Теперь отправь текст")


    @dp.message()
    async def receive_text(message: Message):

        state = user_states.get(message.from_user.id)

        if not state:
            return

        if state["step"] != "text":
            return

        code = state["code"]

        add_post(
            code,
            state["file_id"],
            message.text
        )

        user_states.pop(message.from_user.id)

        await message.answer("✅ Пост добавлен")
