import asyncio
import time
from aiogram import Bot
from modules.quiz_storage import load_questions, load_results, save_results
from modules.quiz_image import create_scoreboard_image


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
                correct_users.append({
                    "uid": uid,
                    "name": data["name"],
                    "time": data["time"]
                })
    
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
    
                uid = user["uid"]
    
                if uid not in self.state["scoreboard"]:
                    self.state["scoreboard"][uid] = {
                        "name": user["name"],
                        "score": 0
                    }
    
                self.state["scoreboard"][uid]["score"] += points[i]
    
        # правильный ответ
        correct_option = self.questions[index]["options"][correct]
        text += f"\n✅ <b>{correct_option}</b>\n🤝 <i><b>Sponsored by Et Vivit</b></i>"
    
        # рейтинг
        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
    
        if scores:
            text += "\n\n🏆 <b>Рейтинг:</b>\n"
    
            for i, (uid, data) in enumerate(scores[:5]):
                text += f"{i+1}. {data['name']} — <b>{data['score']}</b>\n"

        # ===== ТЕСТ КАРТИНКИ =====
        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        top_players = [
            (uid, data["name"], data["score"])
            for uid, data in scores[:3]
        ]
        
        try:
            image = await create_scoreboard_image(self.bot, top_players)
        
            await self.bot.send_photo(
                self.group_id,
                photo=image,
                caption="🔥 Тест рейтинга"
            )
        except Exception as e:
            print("IMAGE TEST ERROR:", e)
        await self.bot.send_message(self.group_id, text)
       
    # ===== FINISH QUIZ =====

    async def finish_quiz(self):

        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
    
        # 🏆 ТОП-3 для картинки
        top_players = [
            (uid, data["name"], data["score"])
            for uid, data in scores[:3]
        ]
    
        # 🎨 картинка
        try:
            image = await create_scoreboard_image(self.bot, top_players)
    
            await self.bot.send_photo(
                self.group_id,
                photo=image,
                caption="🏆 Финальный рейтинг"
            )
        except Exception as e:
            print("IMAGE ERROR:", e)
    
        await asyncio.sleep(2)
    
        # 📝 текст
        text = "🏁 <b>QUIZBALL ЗАВЕРШЁН!</b>\n\n"
    
        if scores:
            uid, data = scores[0]
            text += f"🏆 <b>ЧЕМПИОН:</b>\n🥇 {data['name']} — {data['score']} очков\n\n"
    
        text += "🔥 <b>ТОП-3:</b>\n"
    
        medals = ["🥇", "🥈", "🥉"]
    
        for i, (uid, data) in enumerate(scores[:3]):
            text += f"{medals[i]} {data['name']} — {data['score']}\n"
    
        text += "\n👏 Спасибо за игру!"
    
        await self.bot.send_message(self.group_id, text)
    
        # 💾 сохранение
        results = load_results()
        results[self.state["date"]] = self.state["scoreboard"]
        save_results(results)
    
        self.state["active"] = False
