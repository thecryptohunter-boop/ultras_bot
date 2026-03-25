import os

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.filters import Command

from modules.config import ADMINS
import json

try:
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
except:
    await message.answer("❌ JSON битый!")
    return

print("JSON MANAGER LOADED")

router = Router()

user_states = {}

CATEGORIES_PATH = "data/categories.json"
EVENTS_PATH = "events.json"
QUIZ_FILE = "data/quiz_questions.json"

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
            ],

            [
                InlineKeyboardButton(
                    text="⚽ Скачать QUIZ",
                    callback_data="json_quiz_download"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⚽ Загрузить QUIZ",
                    callback_data="json_quiz_upload"
                )
            ]
        ]
    )

    await message.answer(
        "📂 Управление JSON",
        reply_markup=keyboard
    )


# ===== CALLBACK HANDLER =====
@router.callback_query(lambda c: c.data.startswith("json_quiz_"))
async def quiz_json_handler(callback: CallbackQuery):

    if callback.from_user.id not in ADMINS:
        return

    action = callback.data.split("_")[-1]

    # ===== СКАЧАТЬ =====
    if action == "download":

        try:
            await callback.message.answer_document(
                document=FSInputFile(QUIZ_FILE),
                caption="⚽ quiz_questions.json"
            )
        except Exception as e:
            await callback.message.answer(f"❌ Ошибка: {e}")

    # ===== ЗАГРУЗИТЬ =====
    elif action == "upload":

        user_states[callback.from_user.id] = {
            "action": "upload_quiz"
        }

        await callback.message.answer(
            "📤 Отправь файл quiz_questions.json"
        )

    await callback.answer()

@router.callback_query(F.data.startswith("json_"))
async def json_callbacks(callback: CallbackQuery, bot):

    if callback.from_user.id not in ADMINS:
        return

    data = callback.data

    # ===== DOWNLOAD CATEGORIES =====

    if data == "json_download_categories":

        if not os.path.exists(CATEGORIES_PATH):

            await callback.message.answer("❌ Файл categories.json не найден")
            await callback.answer()
            return

        file = FSInputFile(CATEGORIES_PATH)

        await bot.send_document(
            callback.message.chat.id,
            document=file
        )

        await callback.message.answer("✅ Файл categories.json скачан")

        await callback.answer()

        return


    # ===== DOWNLOAD EVENTS =====

    if data == "json_download_events":

        if not os.path.exists(EVENTS_PATH):

            await callback.message.answer("❌ Файл events.json не найден")
            await callback.answer()
            return

        file = FSInputFile(EVENTS_PATH)

        await bot.send_document(
            callback.message.chat.id,
            document=file
        )

        await callback.message.answer("✅ Файл events.json скачан")

        await callback.answer()

        return


    # ===== UPLOAD CATEGORIES =====

    if data == "json_upload_categories":

        user_states[callback.from_user.id] = "upload_categories"

        await callback.message.answer(
            "📤 Отправь файл categories.json"
        )

        await callback.answer()

        return


    # ===== UPLOAD EVENTS =====

    if data == "json_upload_events":

        user_states[callback.from_user.id] = "upload_events"

        await callback.message.answer(
            "📤 Отправь файл events.json"
        )

        await callback.answer()

        return

# ===== FILE QUIZ UPLOAD =====
@router.message(lambda m: m.document)
async def handle_quiz_upload(message: Message):

    if message.from_user.id not in ADMINS:
        return

    state = user_states.get(message.from_user.id)

    if not state or state.get("action") != "upload_quiz":
        return

    file = message.document

    if not file.file_name.endswith(".json"):
        await message.answer("❌ Нужен JSON файл")
        return

    path = QUIZ_FILE

    await message.bot.download(file, destination=path)

    user_states.pop(message.from_user.id)

    await message.answer("✅ quiz_questions.json обновлён")

# ===== FILE CATEGORIES UPLOAD =====

@router.message(F.document)
async def upload_json(message: Message, bot):

    if message.from_user.id not in ADMINS:
        return

    state = user_states.get(message.from_user.id)

    if not state:
        return

    doc = message.document


    # ===== CATEGORIES =====

    if state == "upload_categories":

        if doc.file_name != "categories.json":

            await message.answer("❌ Нужно отправить файл categories.json")
            return

        file = await bot.get_file(doc.file_id)

        await bot.download_file(
            file.file_path,
            CATEGORIES_PATH
        )

        await message.answer("✅ categories.json загружен на сервер")


    # ===== EVENTS =====

    elif state == "upload_events":

        if doc.file_name != "events.json":

            await message.answer("❌ Нужно отправить файл events.json")
            return

        file = await bot.get_file(doc.file_id)

        await bot.download_file(
            file.file_path,
            EVENTS_PATH
        )

        await message.answer("✅ events.json загружен на сервер")


    user_states.pop(message.from_user.id, None)
