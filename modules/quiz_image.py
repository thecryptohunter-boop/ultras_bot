from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO


async def create_scoreboard_image(bot, top_players):

    width = 800
    height = 400

    img = Image.new("RGB", (width, height), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()

    y = 50

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, name, score) in enumerate(top_players[:3]):

        # получаем аватар
        try:
            photos = await bot.get_user_profile_photos(user_id)

            file_id = photos.photos[0][0].file_id
            file = await bot.get_file(file_id)

            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

            response = requests.get(file_url)
            avatar = Image.open(BytesIO(response.content)).resize((80, 80))

        except:
            avatar = Image.new("RGB", (80, 80), (100, 100, 100))

        img.paste(avatar, (50, y))

        text = f"{medals[i]} {name} — {score}"

        draw.text((150, y + 25), text, fill=(255, 255, 255), font=font)

        y += 100

    output = BytesIO()
    output.name = "scoreboard.png"

    img.save(output, format="PNG")
    output.seek(0)

    return output
