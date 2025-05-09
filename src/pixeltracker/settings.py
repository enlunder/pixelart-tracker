import logging

from pydantic import BaseSettings, Field, HttpUrl


class Settings(BaseSettings):
    # YouTube viewer settings
    YOUTUBE_API_HOST: HttpUrl = Field(
        default="https://www.googleapis.com/youtube/v3/channels?part=statistics",
        description="URL of the reference to connect through YouTube.",
    )
    YOUTUBE_CHANNEL_ID = Field(
        default="",
        description="Youtube Channel to check the subscribers.",
    )
    YOUTUBE_API_KEY = Field(
        default="",
        description="Youtube Data API Key to use on requests.",
    )

    # Crypto settings
    CRYPTO_API_HOST: HttpUrl = Field(
        default="https://api.coingecko.com/api/v3",
        description="URL of the reference to track cryptocurrencies data.",
    )
    CRYPTO_CURRENCIES = Field(
        default="bitcoin,ethereum",
        description="Cryptocurrencies symbols split by commas.",
    )
    FINANCE_TICKERS = Field(
        default="GC=F,EURUSD=X",
        description="Yahoo Finance tickers split by commas.", 
    )
    # General settings
    TILES = Field(
        default="crypto,finance",
        description="Amount of tiles to show in loop.",
    )
    REFRESH_TIME = Field(
        default=30,
        description="Refresh time amount in seconds to refresh the screen image with the next tile.",
    )
    LOG_LEVEL = Field(
        default=logging.INFO,
        description="Default log level for different packages",
    )

    class Config:
        env_prefix = "SUBS_"
        case_sensitive = False
        env_file = ".env"


settings = Settings()
