import asyncio
import time
from aiogram import Bot
from modules.quiz_storage import load_questions, load_results, save_results


class QuizEngine:

    def __init__(self, bot: Bot, group_id: int):
        self.bot = bot
        self.group_id = group_id

        self.state = {
            "active": False,
            "date": None,
            "question_index": 0,
            "poll_id": None,
            "poll_message_id": None,
            "start_time": None,
            "answer_times": {},
            "scoreboard": {}
        }

        self.questions = []
  
  
    # ===== START QUIZ =====

    async def start_quiz(self, date):

        if self.state["active"]:
            return

        self.questions = load_questions(date)

        if not self.questions:
            await self.bot.send_message(self.group_id, "❌ Нет вопросов на эту дату")
            return

        self.state["active"] = True
        self.state["date"] = date
        self.state["question_index"] = 0
        self.state["scoreboard"] = {}

        # ⏳ Обратный отсчёт
        msg = await self.bot.send_message(
            self.group_id,
            "⚽ <b>QUIZBALL</b>\n\n⏳ Старт через 10 секунд..."
        )

        for i in range(10, 0, -1):
            await asyncio.sleep(1)
            await msg.edit_text(
                f"⚽ <b>QUIZBALL</b>\n\n⏳ Старт через {i} сек..."
            )

        await msg.edit_text("🔥 <b>ПОЕХАЛИ!</b>")

        await asyncio.sleep(1)

        asyncio.create_task(self.send_question())

    # ===== SEND QUESTION =====

    async def send_question(self):

        if not self.state["active"]:
            return

        index = self.state["question_index"]

        print(f"➡️ QUESTION {index+1}")

        if index >= len(self.questions):
            await self.finish_quiz()
            return

        q = self.questions[index]

        await self.bot.send_message(
            self.group_id,
            "⚡ Побеждает самый быстрый — не жди чужих ответов!\n\n"
            f"⁉️<b>Вопрос {index+1}/10</b>"
        )

        poll = await self.bot.send_poll(
            chat_id=self.group_id,
            question=q["question"],
            options=q["options"],
            type="regular",
            is_anonymous=False
        )

        self.state["poll_id"] = poll.poll.id
        self.state["poll_message_id"] = poll.message_id
        self.state["start_time"] = time.time()
        self.state["answer_times"] = {}

        await asyncio.sleep(30)

        await self.close_poll()

    # ===== CLOSE POLL =====

    async def close_poll(self):

        print("⛔ CLOSING POLL")

        try:
            poll = await self.bot.stop_poll(
                self.group_id,
                self.state["poll_message_id"]
            )
        except Exception as e:
            print("STOP POLL ERROR:", e)
            poll = None

        try:
            await self.calculate_results()
        except Exception as e:
            print("CALC ERROR:", e)

        self.state["question_index"] += 1

        await asyncio.sleep(3)

        asyncio.create_task(self.send_question())

    # ===== REGISTER ANSWER =====

    async def register_answer(self, user_id, name, option):

        if not self.state["active"]:
            return

        if user_id in self.state["answer_times"]:
            return

        response_time = time.time() - self.state["start_time"]

        self.state["answer_times"][user_id] = {
            "name": name,
            "option": option,
            "time": response_time
        }

    # ===== CALCULATE RESULTS =====

    async def calculate_results(self):

        index = self.state["question_index"]
        correct = self.questions[index]["correct"]

        correct_users = []

        for uid, data in self.state["answer_times"].items():
            if data["option"] == correct:
                correct_users.append(data)

        sorted_users = sorted(correct_users, key=lambda x: x["time"])
        top3 = sorted_users[:3]

        points = [3, 2, 1]
        medals = ["🥇", "🥈", "🥉"]

        text = f"❓ <b>Вопрос {index+1} завершён</b>\n\n"

        # ТОП игроков
        if not top3:
            text += "😬 Никто не угадал\n"
        else:
            for i, user in enumerate(top3):
                text += f"{medals[i]} {user['name']} (+{points[i]})\n"

                self.state["scoreboard"].setdefault(user["name"], 0)
                self.state["scoreboard"][user["name"]] += points[i]

        # правильный ответ
        correct_option = self.questions[index]["options"][correct]
        text += f"\n✅ <b>{correct_option}</b>\n\n\n🤝 <i>Sponsored by Et Vivit</i>"
        
        # рейтинг
        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        if scores:
            text += "\n🏆 <b>Рейтинг:</b>\n"

            for i, (name, score) in enumerate(scores[:5]):
                text += f"{i+1}. {name} — <b>{score}</b>\n"

        await self.bot.send_message(self.group_id, text)

    # ===== FINISH =====

    async def finish_quiz(self):

        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        await asyncio.sleep(2)

        text = "🏁 <b>QUIZBALL ЗАВЕРШЁН!</b>\n\n"

        if scores:
            name, score = scores[0]
            text += f"🏆 <b>ЧЕМПИОН:</b>\n🥇 {name} — {score} очков\n\n"

        text += "🔥 <b>ТОП-3:</b>\n"

        medals = ["🥇", "🥈", "🥉"]

        for i, (name, score) in enumerate(scores[:3]):
            text += f"{medals[i]} {name} — {score}\n"

        text += "\n👏 Спасибо за игру!"

        await self.bot.send_message(self.group_id, text)

        results = load_results()
        results[self.state["date"]] = self.state["scoreboard"]
        save_results(results)

        self.state["active"] = False
