import os
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from modules.config import ADMINS

router = Router()

user_states = {}

CATEGORIES_PATH = "data/categories.json"
EVENTS_PATH = "events.json"
QUIZ_PATH = "data/quiz_questions.json"


# ===== MENU =====
@router.message(Command("json"))
async def json_menu(message: Message):

    if message.from_user.id not in ADMINS:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [InlineKeyboardButton(text="⬇️ categories", callback_data="json_download_categories")],
            [InlineKeyboardButton(text="⬇️ events", callback_data="json_download_events")],
            [InlineKeyboardButton(text="⬇️ quiz", callback_data="json_download_quiz")],

            [InlineKeyboardButton(text="⬆️ categories", callback_data="json_upload_categories")],
            [InlineKeyboardButton(text="⬆️ events", callback_data="json_upload_events")],
            [InlineKeyboardButton(text="⬆️ quiz", callback_data="json_upload_quiz")],
        ]
    )

    await message.answer("📂 JSON MANAGER", reply_markup=keyboard)


# ===== CALLBACK =====
@router.callback_query(F.data.startswith("json_"))
async def json_callbacks(callback: CallbackQuery, bot):

    if callback.from_user.id not in ADMINS:
        return

    data = callback.data
    user_id = callback.from_user.id

    # ===== DOWNLOAD =====

    if data == "json_download_categories":
        path = CATEGORIES_PATH

    elif data == "json_download_events":
        path = EVENTS_PATH

    elif data == "json_download_quiz":
        path = QUIZ_PATH

    else:
        path = None

    if path:
        if not os.path.exists(path):
            await callback.message.answer("❌ Файл не найден")
        else:
            await bot.send_document(callback.message.chat.id, FSInputFile(path))
        await callback.answer()
        return

    # ===== UPLOAD =====

    if data == "json_upload_categories":
        user_states[user_id] = {"action": "upload_categories"}

    elif data == "json_upload_events":
        user_states[user_id] = {"action": "upload_events"}

    elif data == "json_upload_quiz":
        user_states[user_id] = {"action": "upload_quiz"}

    else:
        return

    await callback.message.answer("📤 Отправь JSON файл")
    await callback.answer()


# ===== FILE UPLOAD =====
@router.message(F.document)
async def handle_upload(message: Message, bot):

    if message.from_user.id not in ADMINS:
        return

    state = user_states.get(message.from_user.id)

    if not isinstance(state, dict):
        return

    action = state.get("action")
    doc = message.document

    if not doc.file_name.endswith(".json"):
        await message.answer("❌ Нужен JSON файл")
        return

    # ===== PATH =====

    if action == "upload_categories":
        path = CATEGORIES_PATH

    elif action == "upload_events":
        path = EVENTS_PATH

    elif action == "upload_quiz":
        path = QUIZ_PATH

    else:
        return

    # ===== DOWNLOAD FILE =====

    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, path)

    # ===== VALIDATE JSON =====

    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
    except:
        await message.answer("❌ JSON битый!")
        return

    user_states.pop(message.from_user.id, None)

    await message.answer("✅ Файл загружен")
