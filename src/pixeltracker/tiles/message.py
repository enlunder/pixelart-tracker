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

import asyncio

class Message(IDotMatrixTile):
    message: str

    def __init__(self, idms: IDotMatrixScreen, message: str, test: bool):
        super().__init__(idms, test)
        self.message = message

    async def run(self):
        current = Path(__file__).parent.resolve()
        font_path = current / f"../resources/org_01.ttf"
        await self.send_text(self.message, font_path)
    
    async def get_data(self):
        pass
    
    def create_image(self, text: str, image_path: Path):
        pass
        
