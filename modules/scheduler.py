import asyncio
from datetime import datetime

from category_manager import post_category
from storage import load_categories


async def scheduler(post_today):

    print("SCHEDULER STARTED")

    last_today = None
    last_category = {}

    while True:

        now = datetime.now()

        # TODAY
        if now.hour == 9 and now.minute == 0:

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

                    await post_category(code)

        await asyncio.sleep(30)
