import asyncio
from datetime import datetime

from modules.storage import load_categories
from modules.category_manager import post_category


async def scheduler(post_today, bot, CHANNEL_ID, ADMINS):

    print("SCHEDULER STARTED")

    last_today = None
    last_category = {}

    while True:

        now = datetime.now()

        # TODAY

        if now.hour == 16 and now.minute == 56:

            if last_today != now.date():

                last_today = now.date()

                await post_today()

        # РУБРИКИ

        data = load_categories()

        for code, cat in data.items():

            if (
                now.weekday() == cat["day"]
                and now.hour == cat["hour"]
                and now.minute == cat["minute"]
            ):

                if last_category.get(code) != now.date():

                    last_category[code] = now.date()

                    await post_category(bot, CHANNEL_ID, ADMINS, code)

        await asyncio.sleep(30)
