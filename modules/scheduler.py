import asyncio
from datetime import datetime

from storage import load_categories
from category_manager import post_category


async def category_scheduler():

    while True:

        now = datetime.now()
        weekday = now.weekday()

        data = load_categories()

        for name, cat in data.items():

            if (
                cat["day"] == weekday
                and cat["hour"] == now.hour
                and cat["minute"] == now.minute
            ):

                await post_category(name)

        await asyncio.sleep(60)
