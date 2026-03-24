import asyncio
from datetime import datetime

from modules.storage import load_categories
from modules.category_manager import post_category
from zoneinfo import ZoneInfo
from modules.config import TOKEN, CHANNEL_ID, ADMINS


async def scheduler(post_today, bot, CHANNEL_ID, ADMINS):

    print("SCHEDULER STARTED")

    last_today = None
    last_category = {}

    while True:

        now = datetime.now()

        # TODAY

        if now.hour == 8 and now.minute == 0:

            if last_today != now.date():

                last_today = now.date()

                await post_today()

        # КАТЕГОРИИ

        data = load_categories()
        print("CATEGORIES:", data.keys())
        print("TIME:", now.hour, now.minute, "weekday:", now.weekday())
        for code, cat in data.items():

            day = cat["day"]

            if isinstance(day, list):
                day_match = now.weekday() in day
            else:
                day_match = now.weekday() == day

            if (
                day_match
                and now.hour == cat["hour"]
                and abs(now.minute - cat["minute"]) <= 1
            ):

                if last_category.get(code) != now.date():

                    last_category[code] = now.date()

                    await post_category(bot, CHANNEL_ID, ADMINS, code)

        await asyncio.sleep(30)
