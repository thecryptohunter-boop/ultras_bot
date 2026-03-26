from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from aiogram.types import BufferedInputFile


async def create_scoreboard_image(bot, top_players):

    width = 900
    height = 500

    # 🌌 КИБЕР ФОН
    img = Image.new("RGB", (width, height), (10, 10, 25))
    draw = ImageDraw.Draw(img)

    # 🅰️ ШРИФТЫ
    title_font = ImageFont.truetype("assets/ARIALBD.TTF", 44)
    name_font = ImageFont.truetype("assets/ARIAL.TTF", 28)
    score_font = ImageFont.truetype("assets/ARIAL.TTF", 32)

    # 🔥 ЗАГОЛОВОК
    draw.text((width//2 - 140, 30), "QUIZBALL", fill=(0, 255, 200), font=title_font)

    y = 120

    # 🎨 цвета медалей
    medal_colors = [
        (255, 215, 0),    # gold
        (180, 180, 180),  # silver
        (205, 127, 50)    # bronze
    ]

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
            avatar = Image.new("RGB", (90, 90), (80, 80, 80))

        img.paste(avatar, (60, y))

        # ===== МЕДАЛЬ (КРУГ) =====
        x_medal = 180
        y_medal = y + 25

        draw.ellipse(
            (x_medal, y_medal, x_medal+40, y_medal+40),
            fill=medal_colors[i]
        )

        draw.text(
            (x_medal+12, y_medal+5),
            str(i+1),
            fill=(0, 0, 0),
            font=score_font
        )

        # ===== ИМЯ =====
        draw.text((250, y+25), name, fill=(255, 255, 255), font=name_font)

        # ===== ОЧКИ (НЕОН) =====
        draw.text((720, y+25), f"{score}", fill=(0, 255, 200), font=score_font)

        y += 110

    # 📦 ВЫГРУЗКА
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return BufferedInputFile(output.getvalue(), filename="score.png")
