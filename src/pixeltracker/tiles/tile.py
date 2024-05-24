import logging
import math
from abc import ABC, abstractmethod
from decimal import Decimal
from pathlib import Path
from typing import Union

import aiohttp

# idotmatrix imports
from ..screen import IDotMatrixScreen

logger = logging.getLogger(__name__)


class IDotMatrixTile(ABC):
    test: bool = False
    idms: IDotMatrixScreen

    def __init__(self, idms: IDotMatrixScreen, test=False):
        self.idms = idms
        self.test = test

    @abstractmethod
    async def get_data(self):
        pass

    async def get_json(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    def format_number(self, number: Union[int, Decimal]) -> str:
        if not isinstance(number, Decimal):
            decimal_number = Decimal(number)
        else:
            decimal_number = number

        if 1 <= number < 100 and decimal_number % 1 != 0:
            text = str(round(decimal_number, 2))
        elif 100 <= number < 1000 and decimal_number % 1 != 0:
            text = str(round(decimal_number, 1))
        elif 1000 <= number < 10000:
            decimal_number = decimal_number / Decimal(1000)
            text = str(round(decimal_number, 2)) + "K"
        elif 10000 <= number < 100000:
            decimal_number = decimal_number / Decimal(1000)
            text = str(round(decimal_number, 1)) + "K"
        elif 100000 <= number < 1000000:
            decimal_number = decimal_number / Decimal(1000)
            text = str(round(decimal_number, 1)) + "K"
        elif 1000000 <= number < 10000000:
            decimal_number = decimal_number / Decimal(1000000)
            text = str(round(decimal_number, 2)) + "M"
        elif 10000000 <= number < 100000000:
            decimal_number = decimal_number / Decimal(1000000)
            text = str(round(decimal_number, 1)) + "M"
        elif 100000000 <= number < 1000000000:
            decimal_number = decimal_number / Decimal(1000000)
            text = str(round(decimal_number, 1)) + "M"
        else:
            text = str(decimal_number)

        return text.replace(".", ",")

    def get_text_initial_position(self, text: str) -> int:
        chars = len(text)
        total_screen_size = 32  # 32pxx32px screen
        offset = 0
        if text.count(",") >= 1:
            offset = -2
        if text.count("M") >= 1:
            offset = offset + 1
        total_pixels = (chars * 4) + (chars - 1) + offset  # 4px per character + 1px between characters + offset

        return max(math.floor((total_screen_size - total_pixels) / 2), 0)

    async def send(self, image_path: Path, process_image: bool):
        await self.idms.set_image(image_path, process_image)
        logger.debug(f"Sent image to screen: {image_path}")

    @abstractmethod
    def create_image(self, text: str, image_path: Path):
        pass

    @abstractmethod
    async def run(self):
        await self.get_data()
