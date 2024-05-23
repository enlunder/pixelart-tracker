import math
from pathlib import Path

import aiohttp
import logging

from decimal import *
from PIL import Image, ImageDraw, ImageFont

from settings import settings

logger = logging.getLogger(__name__)


async def get_json(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def youtube_subscribers(channel_id: str, api_key: str) -> int:
    yt_api_url = settings.API_HOST
    url = f"{yt_api_url}&id={channel_id}&key={api_key}"
    response = await get_json(url)

    items = response["items"]
    if len(items) < 1:
        raise ValueError("Not enough items")

    subscribers = items[0]["statistics"]["subscriberCount"]
    return int(subscribers)


def format_subscribers(subscribers: int) -> str:
    subs = Decimal(str(subscribers))
    if 1000 <= subscribers < 10000:
        subs = subs / Decimal(1000)
        text = str(round(subs, 2)) + "K"
    elif 10000 <= subscribers < 100000:
        subs = subs / Decimal(1000)
        text = str(round(subs, 1)) + "K"
    elif 100000 <= subscribers < 1000000:
        subs = subs / Decimal(1000)
        text = str(round(subs, 1)) + "K"
    elif 1000000 <= subscribers < 10000000:
        subs = subs / Decimal(1000000)
        text = str(round(subs, 2)) + "M"
    elif 10000000 <= subscribers < 100000000:
        subs = subs / Decimal(1000000)
        text = str(round(subs, 1)) + "M"
    elif 100000000 <= subscribers < 1000000000:
        subs = subs / Decimal(1000000)
        text = str(round(subs, 1)) + "M"
    else:
        text = str(subs)

    return text.replace(".", ",")


def get_initial_position(text: str) -> int:
    chars = len(text)
    total_screen_size = 32  # 32pxx32px screen
    offset = 0
    if text.count(",") >= 1:
        offset = -2
    if text.count("M") >= 1:
        offset = offset + 1
    total_pixels = (chars * 4) + (chars - 1) + offset   # 4px per character + 1px between characters + offset

    return math.floor((total_screen_size - total_pixels) / 2)


def create_subscribers_image(text: str, image_path: Path):
    image = Image.open('resources/background-image.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('resources/retro-pixel-petty-5h.ttf', size=5)

    init_x = get_initial_position(text)

    (x, y) = (init_x, 15)
    color = 'rgb(255, 255, 255)'  # black color
    draw.text((x, y), text, fill=color, font=font)
    (x, y) = (6, 23)
    draw.text((x, y), "Subs", fill=color, font=font)

    image.save(image_path)
