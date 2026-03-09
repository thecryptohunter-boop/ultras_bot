from modules.storage import load_categories, save_categories


def add_post(category, file_id, text):

    data = load_categories()

    data[category]["posts"].append({
        "file_id": file_id,
        "text": text
    })

    save_categories(data)


async def post_category(bot, CHANNEL_ID, ADMINS, name):
    print("POST CATEGORY:", name)
    data = load_categories()

    cat = data[name]

    posts = cat["posts"]

    if not posts:
        return

    index = cat["last_index"] + 1

    if index >= len(posts):

        if not cat["finished_notified"]:

            await bot.send_message(
                list(ADMINS)[0],
                f"⚠️ Закончились материалы в рубрике {cat['title']}"
            )

            cat["finished_notified"] = True

            save_categories(data)

        return

    post = posts[index]

    await bot.send_photo(
        CHANNEL_ID,
        photo=post["file_id"],
        caption = f"{cat['title']}\n\n{post['text']}\n\n{cat['tag']}"
    )

    cat["last_index"] = index

    save_categories(data)
