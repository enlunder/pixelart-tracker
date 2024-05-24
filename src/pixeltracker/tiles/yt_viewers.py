import logging
import tempfile
from pathlib import Path
from random import randrange

from PIL import Image, ImageDraw, ImageFont
from ..settings import settings

from .tile import IDotMatrixTile

logger = logging.getLogger("pixelart-tracker")


class YoutubeViewers(IDotMatrixTile):
    subscribers: int = 0
    test_subscribers: int = 0

    async def get_data(self):
        if self.test:
            self.test_subscribers = self.test_subscribers + randrange(1000)
            self.subscribers = self.test_subscribers
            return

        yt_api_url = settings.YOUTUBE_API_HOST
        channel_id = settings.YOUTUBE_CHANNEL_ID
        api_key = settings.YOUTUBE_API_KEY
        url = f"{yt_api_url}&id={channel_id}&key={api_key}"
        response = await self.get_json(url)

        items = response["items"]
        if len(items) < 1:
            raise ValueError("Not enough items")

        subscribers = items[0]["statistics"]["subscriberCount"]

        logger.debug(f"Subscribers obtained from YouTube Data API: {subscribers}")

        self.subscribers = int(subscribers)

    def create_image(self, text: str, image_path: Path):
        current = Path(__file__).resolve()
        background_path = current / f"../../resources/yt-background.png"
        image = Image.open(background_path)
        draw = ImageDraw.Draw(image)
        font_path = current / f"../../resources/retro-pixel-petty-5h.ttf"
        font = ImageFont.truetype(font_path, size=5)
        color = "rgb(255, 255, 255)"  # white color

        init_x = self.get_text_initial_position(text)

        (x, y) = (init_x, 15)
        draw.text((x, y), text, fill=color, font=font)
        (x, y) = (6, 23)
        draw.text((x, y), "Subs", fill=color, font=font)

        image.save(image_path)

    async def run(self):
        await super().run()
        subs_str = self.format_number(self.subscribers)

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png") as tmp_image:
            self.create_image(subs_str, Path(tmp_image.name))
            logger.debug(f"New Image generated: {tmp_image.name}")

            await self.send(Path(tmp_image.name), False)
