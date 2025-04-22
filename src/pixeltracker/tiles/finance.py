import logging
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

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
            # Get current UTC time (or use a specific time)
            current_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            time_24h_ago = current_time - timedelta(hours=24)
            
            # Fetch data using yfinance with 1 hour interval for the last 2 days
            t = yf.Ticker(self.ticker)
            data = t.history(
                start=time_24h_ago - timedelta(hours=1),  # Buffer to ensure coverage
                end=current_time + timedelta(hours=1),
                interval="1h",
                repair=True,
            )           

            # Fetch historical data up until the day before today
            end_date = current_time - timedelta(days=1)
            start_date = end_date - timedelta(days=4)  # 4 days of data, but up to the day before today
            hist = t.history(start=start_date, end=end_date, interval="1d")     
            if hist.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")
            
            # Ensure the index of data is in UTC
            data.index = pd.to_datetime(data.index).tz_localize(None)
            
            # Create empty DataFrame with your desired timestamps
            desired_times = pd.date_range(start=time_24h_ago, end=current_time, freq="h")
            result = pd.DataFrame(index=desired_times, columns=["Close"], dtype=float)
            
            # Reindex data to match the desired times and fill in the values
            data_reindexed = data.reindex(desired_times)
            result.update(data_reindexed[["Close"]])
            logger.debug(result)
            
            # Fill NaN values with the latest available data 
            result = result.ffill()
            
            # Extract values
            latest_price = result["Close"].iloc[-1] if not result.empty else None
            price_24h_ago = result["Close"].iloc[0] if not result.empty else None
            logger.debug(latest_price, price_24h_ago)
            
            # If data is missing, use the latest close price
            if pd.isna(latest_price):
                logger.debug(f"Data was missing, using latest close price")
                latest_price = hist["Close"].iloc[-1]
                price_24h_ago = hist["Close"].iloc[-1]

            # If 24h price is missing, use previous daily close
            if pd.isna(price_24h_ago):
                price_24h_ago = hist["Close"].iloc[-1]
            
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

        if self.price_change_24h > 0:
            price_color = "rgb(0, 255, 0)"
        elif self.price_change_24h < 0:
            price_color = "rgb(255, 0, 0)"
        else: # Unchanged price likely means the market is not open
            price_color = "rgb(255, 255, 255)" 
            
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
