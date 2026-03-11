from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import ADMINS
from aiogram import Bot

router = Router()

user_states = {}

CATEGORIES_PATH = "data/categories.json"
EVENTS_PATH = "events.json"


# ===== JSON MENU =====

@router.message(Command("json"))
async def json_menu(message: Message):

    if message.from_user.id not in ADMINS:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="⬇️ Скачать categories.json",
                    callback_data="json_download_categories"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬇️ Скачать events.json",
                    callback_data="json_download_events"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬆️ Загрузить categories.json",
                    callback_data="json_upload_categories"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬆️ Загрузить events.json",
                    callback_data="json_upload_events"
                )
            ]

        ]
    )

    await message.answer(
        "📂 Управление JSON",
        reply_markup=keyboard
    )


# ===== CALLBACK HANDLER =====

@router.callback_query(F.data.startswith("json_"))
async def json_callbacks(callback: CallbackQuery, bot: Bot):

    if callback.from_user.id not in ADMINS:
        return

    data = callback.data


    # ===== DOWNLOAD CATEGORIES =====

    if data == "json_download_categories":

        await bot.send_document(
            callback.message.chat.id,
            document=CATEGORIES_PATH
        )

        await callback.answer()


    # ===== DOWNLOAD EVENTS =====

    elif data == "json_download_events":

        await bot.send_document(
            callback.message.chat.id,
            document=EVENTS_PATH
        )

        await callback.answer()


    # ===== UPLOAD CATEGORIES =====

    elif data == "json_upload_categories":

        user_states[callback.from_user.id] = "upload_categories"

        await callback.message.answer(
            "📤 Отправь файл categories.json"
        )

        await callback.answer()


    # ===== UPLOAD EVENTS =====

    elif data == "json_upload_events":

        user_states[callback.from_user.id] = "upload_events"

        await callback.message.answer(
            "📤 Отправь файл events.json"
        )

        await callback.answer()



# ===== FILE UPLOAD HANDLER =====

@router.message(F.document)
async def upload_json(message: Message, bot: Bot):

    if message.from_user.id not in ADMINS:
        return

    state = user_states.get(message.from_user.id)

    if not state:
        return

    doc = message.document


    # ===== UPLOAD CATEGORIES =====

    if state == "upload_categories":

        if doc.file_name != "categories.json":

            await message.answer("❌ Нужен файл categories.json")
            return

        file = await bot.get_file(doc.file_id)

        await bot.download_file(
            file.file_path,
            CATEGORIES_PATH
        )

        await message.answer("✅ categories.json обновлён")


    # ===== UPLOAD EVENTS =====

    elif state == "upload_events":

        if doc.file_name != "events.json":

            await message.answer("❌ Нужен файл events.json")
            return

        file = await bot.get_file(doc.file_id)

        await bot.download_file(
            file.file_path,
            EVENTS_PATH
        )

        await message.answer("✅ events.json обновлён")


    user_states.pop(message.from_user.id, None)
