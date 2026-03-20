from aiogram import Router
from aiogram.types import PollAnswer, Message
from modules.config import ADMINS

router = Router()

quiz_engine = None


def setup_quiz(engine):
    global quiz_engine
    quiz_engine = engine


@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):

    if poll_answer.poll_id != quiz_engine.state["poll_id"]:
        return

    user = poll_answer.user

    await quiz_engine.register_answer(
        user.id,
        user.full_name,
        poll_answer.option_ids[0]
    )

@router.message()
async def anti_spam(message: Message):

    if not quiz_engine.state["active"]:
        return

    if message.from_user.id in ADMINS:
        return

    # не трогаем команды
    if message.text and message.text.startswith("/"):
        return

    try:
        await message.delete()
    except:
        pass

    try:
        await message.delete()
    except:
        pass
