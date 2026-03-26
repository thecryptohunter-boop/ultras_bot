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


def create_placeholder(name):
    img = Image.new("RGB", (90, 90), (120, 0, 80))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("assets/ARIALBI.TTF", 36)

    initials = name[:2].upper()

    draw.text((25, 25), initials, fill=(255, 255, 255), font=font)

    return make_circle(img)


async def create_scoreboard_image(bot, top_players):

    width = 900
    height = 500

    # 🌈 ГРАДИЕНТ (фиолет → вишня)
    img = Image.new("RGB", (width, height), "#1a0033")
    draw = ImageDraw.Draw(img)

    for i in range(height):
        r = int(50 + (i / height) * 120)
        g = 0
        b = int(80 + (i / height) * 60)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # 🅰️ ШРИФТЫ
    title_font = ImageFont.truetype("assets/ARIALBD.TTF", 44)
    name_font = ImageFont.truetype("assets/ARIAL.TTF", 28)
    score_font = ImageFont.truetype("assets/ARIAL.TTF", 32)

    # 🏆 Заголовок
    draw.text((width//2 - 150, 30), "QUIZBALL", font=title_font, fill=(255, 100, 255))

    y = 130

    colors = [
        (255, 100, 255),  # 1 место — неон розовый
        (180, 120, 255),
        (140, 80, 200)
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
                avatar = make_circle(avatar)
            else:
                avatar = create_placeholder(name)

        except:
            avatar = create_placeholder(name)

        img.paste(avatar, (80, y), avatar)

        # ===== КАРТОЧКА =====
        draw.rounded_rectangle(
            [(180, y), (800, y + 90)],
            radius=20,
            fill=(30, 0, 60)
        )

        # ===== МЕСТО =====
        draw.text(
            (200, y + 25),
            f"{i+1}",
            font=score_font,
            fill=colors[i]
        )

        # ===== ИМЯ =====
        draw.text(
            (260, y + 25),
            name[:14],
            font=name_font,
            fill=(255, 255, 255)
        )

        # ===== ОЧКИ =====
        draw.text(
            (720, y + 25),
            str(score),
            font=score_font,
            fill=(255, 120, 255)
        )

        y += 110

    # 📦 OUTPUT
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return BufferedInputFile(output.getvalue(), filename="score.png")
