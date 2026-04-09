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

    # ===== РАМКА =====
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline="white", width=3) 
    
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


# ===== CHAMPION CARD =======


async def create_champion_card(bot, user_id, name, score):

    WIDTH, HEIGHT = 800, 1000

    # ===== ФОН (фиолетово-вишнёвый градиент) =====
    img = Image.new("RGB", (WIDTH, HEIGHT), "#1a002b")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        r = int(40 + y * 0.1)
        g = 0
        b = int(80 + y * 0.15)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


    # ===== ШРИФТЫ =====
    font_big = ImageFont.truetype("assets/ARIALBD.TTF", 60)
    font_mid = ImageFont.truetype("assets/ARIAL.TTF", 40)

    # ===== CHAMPION =====
    title = "CHAMPION"
    w = draw.textlength(title, font=font_big)
    draw.text(((WIDTH - w) / 2, 60), title, fill="white", font=font_big)

    # ===== ЛИНИЯ =====
    line_width = int(w * 1.8)
    draw.line(
        [
            (WIDTH//2 - line_width//2, 140),
            (WIDTH//2 + line_width//2, 140)
        ],
        fill="white",
        width=4
    )

    # ===== АВАТАР =====
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)

        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            avatar_bytes = await bot.download_file(file.file_path)

            avatar = Image.open(BytesIO(avatar_bytes.read())).resize((200, 200))
        else:
            avatar = Image.new("RGB", (200, 200), "gray")

    except:
        avatar = Image.new("RGB", (200, 200), "gray")

    img.paste(avatar, (WIDTH//2 - 100, 180))

    # ===== ИМЯ =====
    name_text = name.upper()
    w = draw.textlength(name_text, font=font_mid)
    draw.text(((WIDTH - w) / 2, 420), name_text, fill="white", font=font_mid)

    # ===== ОЧКИ =====
    score_text = f"{score} ОЧКОВ!"
    w = draw.textlength(score_text, font=font_big)
    draw.text(((WIDTH - w) / 2, 480), score_text, fill="white", font=font_big)

    # ===== КАРТИНКА СНИЗУ =====
    try:
        bottom = Image.open("images/champion.png").resize((600, 250))
        img.paste(bottom, (WIDTH//2 - 300, 650))
    except:
        pass  # если нет — просто пропускаем

    # ===== OUTPUT =====
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return BufferedInputFile(buffer.read(), filename="champion.png")
