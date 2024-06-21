import logging
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from ..screen import IDotMatrixScreen
from ..settings import settings

from .tile import IDotMatrixTile

logger = logging.getLogger("pixelart-tracker")


class Crypto(IDotMatrixTile):
    crypto: str
    symbol: Optional[str] = None
    price: Decimal = Decimal(0)
    price_change_24h: Decimal = Decimal(0)

    def __init__(self, idms: IDotMatrixScreen, crypto: str, test: bool):
        super().__init__(idms, test)
        self.crypto = crypto.lower()

    async def get_data(self):
        base_url = settings.CRYPTO_API_HOST
        url = f"{base_url}/coins/{self.crypto}"
        response = await self.get_json(url)

        crypto_name = response["name"]
        logger.debug(f"Obtained data for {crypto_name}")

        price = response["market_data"]["current_price"]["usd"]
        price_24h_change = response["market_data"]["price_change_percentage_24h"]

        item = response["symbol"]
        if not item:
            raise ValueError("Not enough items")

        logger.debug(f"Price obtained from CoinGecko API: {price}")

        self.symbol = item.lower()
        self.price = Decimal(str(price))
        self.price_change_24h = Decimal(str(price_24h_change))

    def create_image(self, text: str, image_path: Path):
        current = Path(__file__).resolve()
        background_path = current / f"../../resources/{self.crypto}-background.png"
        image = Image.open(background_path)
        draw = ImageDraw.Draw(image)
        font_path = current / f"../../resources/retro-pixel-petty-5h.ttf"
        font = ImageFont.truetype(font_path, size=5)
        color = "rgb(255, 255, 255)"  # symbol in white color
        if self.price_change_24h >= 0:
            price_color = "rgb(0, 255, 0)"
        else:
            price_color = "rgb(255, 0, 0)"

        init_x = self.get_text_initial_position(self.symbol)
        (x, y) = (init_x, 16)
        draw.text((x, y), self.symbol, fill=color, font=font)

        init_x = self.get_text_initial_position(text)

        (x, y) = (init_x, 23)
        draw.text((x, y), text, fill=price_color, font=font)

        image.save(image_path)

    async def run(self):
        await self.get_data()
        price = self.format_number(self.price)
        price_str = f"${price}"

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmp_image:
            self.create_image(price_str, Path(tmp_image.name))
            logger.debug(f"New Image generated: {tmp_image.name}")

            await self.send(Path(tmp_image.name), False)
            tmp_image.close()
            os.unlink(tmp_image.name)
