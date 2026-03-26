from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from aiogram.types import BufferedInputFile


async def create_scoreboard_image(bot, top_players):

    width = 900
    height = 500

    # 🎨 светлый фон
    img = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    # 🅰️ шрифты
    title_font = ImageFont.truetype("assets/ARIAL.TTF", 40)
    name_font = ImageFont.truetype("assets/ARIAL.TTF", 28)
    score_font = ImageFont.truetype("assets/ARIAL.TTF", 32)

    # 🏆 заголовок
    draw.text((width // 2 - 150, 30), "QUIZBALL", fill=(20, 20, 20), font=title_font)

    y = 120

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, name, score) in enumerate(top_players[:3]):

        # ===== АВАТАР =====
        try:
            photos = await bot.get_user_profile_photos(user_id)

            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id
                file = await bot.get_file(file_id)
                file_bytes = await bot.download_file(file.file_path)

                avatar = Image.open(file_bytes).resize((90, 90))
            else:
                raise Exception()

        except:
            # fallback (если нет аватара)
            avatar = Image.new("RGB", (90, 90), (200, 200, 200))

        img.paste(avatar, (80, y))

        # 🥇 медаль
        draw.text((200, y + 20), medals[i], font=score_font, fill=(0, 0, 0))

        # 👤 имя
        draw.text((260, y + 20), name, font=name_font, fill=(0, 0, 0))

        # 🔢 очки
        draw.text((700, y + 20), f"{score}", font=score_font, fill=(0, 120, 255))

        y += 110

    # 📦 сохраняем
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return BufferedInputFile(output.getvalue(), filename="score.png")
