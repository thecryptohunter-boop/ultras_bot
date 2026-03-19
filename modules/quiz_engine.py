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

    async def start_quiz(self, date):
        print("DATE:", date)
        print("QUESTIONS:", self.questions)
        self.questions = load_questions(date)

        if not self.questions:
            return
        if self.state["active"]:
            return 
            
        self.state["active"] = True
        self.state["date"] = date
        self.state["question_index"] = 0
        self.state["scoreboard"] = {}

        await self.bot.send_message(
            self.group_id,
            "⚽ QUIZBALL начинается!\n\n10 вопросов.\n30 секунд на каждый."
        )

        await self.send_question()

    async def send_question(self):

        index = self.state["question_index"]

        if index >= len(self.questions):

            await self.finish_quiz()
            return

        q = self.questions[index]

        poll = await self.bot.send_poll(
            chat_id=self.group_id,
            question=f"Вопрос {index+1}/10\n\n{q['question']}",
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct"],
            is_anonymous=False
        )

        self.state["poll_id"] = poll.poll.id
        self.state["poll_message_id"] = poll.message_id
        self.state["start_time"] = time.time()
        self.state["answer_times"] = {}

        await asyncio.sleep(30)

        await self.close_poll()

    async def close_poll(self):

        await self.bot.stop_poll(
            self.group_id,
            self.state["poll_message_id"]
        )

        await self.calculate_results()

        self.state["question_index"] += 1

        await asyncio.sleep(5)

        await self.send_question()

    async def register_answer(self, user_id, name, option):

        if not self.state["active"]:
            return


        response_time = time.time() - self.state["start_time"]

        self.state["answer_times"][user_id] = {
            "name": name,
            "option": option,
            "time": response_time
        }

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

        text = "📊 Результаты вопроса\n\n"

        for i, user in enumerate(top3):

            name = user["name"]

            text += f"{i+1}️⃣ {name}\n"

            self.state["scoreboard"].setdefault(name, 0)
            self.state["scoreboard"][name] += points[i]

        await self.bot.send_message(self.group_id, text)

        await self.send_scoreboard()

    async def send_scoreboard(self):

        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        text = "🏆 Общий рейтинг\n\n"

        for name, score in scores[:10]:

            text += f"{name} — {score}\n"

        await self.bot.send_message(self.group_id, text)

    async def finish_quiz(self):

        scores = sorted(
            self.state["scoreboard"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        text = "🏆 Победители QUIZBALL\n\n"

        medals = ["🥇", "🥈", "🥉"]

        for i, (name, score) in enumerate(scores[:3]):

            text += f"{medals[i]} {name} — {score}\n"

        await self.bot.send_message(self.group_id, text)

        results = load_results()

        results[self.state["date"]] = self.state["scoreboard"]

        save_results(results)

        self.state["active"] = False
