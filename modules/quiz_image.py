from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from aiogram.types import BufferedInputFile


def make_circle(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    result = Image.new("RGBA", img.size)
    result.paste(img, (0, 0), mask)
    return result


async def create_scoreboard_image(bot, top_players):

    width = 900
    height = 500

    # 🌌 ГРАДИЕНТ ФОН
    img = Image.new("RGB", (width, height), "#5b549c")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        color = int(20 + (i / height) * 40)
        draw.line([(0, i), (width, i)], fill=(10, color, 40))

    # 🅰️ ШРИФТЫ
    title_font = ImageFont.truetype("assets/ARIALBD.TTF", 44)
    name_font = ImageFont.truetype("assets/ARIAL.TTF", 28)
    score_font = ImageFont.truetype("assets/ARIAL.TTF", 32)

    # 🏆 Заголовок
    draw.text((width//2 - 140, 30), "QUIZBALL", font=title_font, fill=(0, 200, 255))

    y = 130

    # 🎨 цвета мест
    colors = [
        (255, 215, 0),   # золото
        (180, 180, 180), # серебро
        (205, 127, 50)   # бронза
    ]

    for i, (user_id, name, score) in enumerate(top_players[:3]):

        # ===== АВАТАР =====
        try:
            photos = await bot.get_user_profile_photos(user_id)

            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id
                file = await bot.get_file(file_id)
                file_bytes = await bot.download_file(file.file_path)

                avatar = Image.open(file_bytes).resize((90, 90)).convert("RGB")
            else:
                raise Exception()

        except:
            avatar = Image.new("RGB", (90, 90), (80, 80, 80))

        avatar = make_circle(avatar)

        img.paste(avatar, (80, y), avatar)

        # ===== КАРТОЧКА =====
        draw.rounded_rectangle(
            [(180, y), (800, y + 90)],
            radius=20,
            fill=(15, 23, 42)
        )

       # ===== МЕСТО =====
       #draw.text(
       #    (200, y + 25),
       #    f"{i+1}",
       #    font=score_font,
       #    fill=colors[i]
       #)

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
        draw.text(
            (260, y + 25),
            name,
            font=name_font,
            fill=(255, 255, 255)
        )

        # ===== ОЧКИ =====
        draw.text(
            (720, y + 25),
            str(score),
            font=score_font,
            fill=(0, 200, 255)
        )

        y += 110

    # 📦 OUTPUT
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return BufferedInputFile(output.getvalue(), filename="score.png")
