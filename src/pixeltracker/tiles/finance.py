import logging
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

import yfinance as yf
import pandas as pd
from decimal import Decimal

from ..screen import IDotMatrixScreen
from ..settings import settings

from .tile import IDotMatrixTile

logger = logging.getLogger("pixelart-tracker")


class Finance(IDotMatrixTile):
    ticker: str 
    symbol: Optional[str] = None
    price: Decimal = Decimal(0)
    price_change_24h: Decimal = Decimal(0)

    def __init__(self, idms: IDotMatrixScreen, ticker: str, test: bool):
        super().__init__(idms, test)
        self.ticker = ticker

    async def get_data(self):
        try:
            # Fetch data using yfinance with 1 hour interval for the last 2 days
            t = yf.Ticker(self.ticker)
            data = t.history(period="2d", interval="1h")
            
            if data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")
            
            # Ensure the data is sorted by date in descending order
            data = data.sort_index(ascending=False)
            
            # Get the latest closing price
            latest_price = data['Close'].iloc[0]
            
            # Find the same hour 24 hours earlier
            latest_timestamp = data.index[0]
            target_timestamp = latest_timestamp - pd.Timedelta(hours=24)
            
            # Get the price at the same hour 24 hours earlier
            price_24h_ago = data.loc[data.index == target_timestamp, 'Close']
            
            if price_24h_ago.empty:
                raise ValueError(f"No data found for the same hour 24 hours earlier for ticker {self.ticker}")
            
            price_24h_ago = price_24h_ago.iloc[0]
            
            # Calculate the 24-hour price change percentage
            price_24h_change = ((latest_price - price_24h_ago) / price_24h_ago) * 100
            
            self.symbol = t.info["shortName"].replace('/', '')
            self.price = Decimal(str(latest_price))
            self.price_change_24h = Decimal(str(price_24h_change))
            
            logger.debug(f"Obtained data for {self.ticker}")
            logger.debug(f"Price obtained from Yahoo Finance: {self.price}")
            logger.debug(f"24-hour price change: {self.price_change_24h}%")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    def create_image(self, text: str, image_path: Path):
        current = Path(__file__).parent.resolve()
        background_path = current / f"../resources/finance-background.png"
        
        image = Image.open(background_path)
        draw = ImageDraw.Draw(image)
        font_path = current / f"../resources/retro-pixel-petty-5h.ttf"
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
#        price = self.format_number(self.price)
        format_decimal = lambda d: f"{d:.5f}".rstrip('0').rstrip('.')
        price_str = format_decimal(self.price)#str(round(self.price, 3))
#        price_str = f"{price}"
        
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmp_image:
            self.create_image(price_str, Path(tmp_image.name))
            logger.debug(f"New Image generated: {tmp_image.name}")

            await self.send(Path(tmp_image.name), False)
            tmp_image.close()
            os.unlink(tmp_image.name)
